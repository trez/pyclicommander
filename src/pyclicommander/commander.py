import sys
from functools import wraps

from pyclicommander.utils import get_idx
from pyclicommander.exceptions import MissingMandatoryArgument, UnknownFlag, UnknownArgument, UnknownCommand


class Cmd:
    def __init__(self, name, wildcard=False, active=False):
        self._name = name
        self.active = active
        self.info = {}
        self.subcommands = {}
        self.wildcard = wildcard

    def __eq__(self, other):
        return self.name == self.other

    def __repr__(self):
        sub_cmds = [repr(s) for s in self.subcommands.values()]
        return f"{'*' if self.active else ''}{self.name()}=> {sub_cmds}"

    def __getitem__(self, key):
        return self.info.get(key)

    def __setitem__(self, key, val):
        self.info[key] = val

    def name(self):
        string_name = ""
        if self._name is None:
            string_name = ""
        elif self.wildcard:
            string_name = self._name.upper()
        else:
            string_name = self._name.lower()
        return string_name

    def new_subcommand(self, name, wildcard=False):
        new_cmd = Cmd(name, wildcard)
        self.add_subcommand(new_cmd)
        return new_cmd

    def add_subcommand(self, sub_cmd):
        self.subcommands[sub_cmd._name] = sub_cmd

    def get_subcommand(self, sub_cmd):
        wildcard_cmd = None
        for cmd_name, cmd in self.subcommands.items():
            if cmd.wildcard:
                wildcard_cmd = cmd
            elif cmd_name == sub_cmd:
                return cmd
        return wildcard_cmd

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def merge(self, other_cmd):
        if other_cmd.active and not self.active:
            self.activate()
            self._name = other_cmd._name
            self.info = other_cmd.info
            self.wildcard = other_cmd.wildcard

        for subname, subcmd in other_cmd.subcommands.items():
            if cmd := self.subcommands.get(subname):
                cmd.merge(subcmd)
            else:
                self.add_subcommand(subcmd)


class Commander():

    def __init__(self, cmd_name=None):
        self.cmd_name = cmd_name
        self.cmd = Cmd(cmd_name)

    def cli(self, definition):
        def decorator_wrapper_register_cmd(func):
            self.add_cli(definition, func)

            # needed otherwise __doc__ doesn't work.
            @wraps(func)
            def _inner_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return _inner_wrapper

        return decorator_wrapper_register_cmd

    def add_cli(self, definition, func, short_description=None, long_description=None):
        new_cmd = self.__create_cmd(definition, func, short_description, long_description)
        self.cmd.merge(new_cmd)

    def __get_cmd(self, args):
        d = self.cmd
        cmd_args = []
        for i, cmd in enumerate(args):
            if not cmd.startswith('-') and (subcommand := d.get_subcommand(cmd)):
                d = subcommand
                if subcommand.wildcard:
                    cmd_args += [cmd]
            else:
                # matched as far as possible, what is left are arguments to the cmd.
                cmd_args += args[i:]
                break

        if d.active:
            return d, cmd_args

    def __create_cmd(self, definition, func, short_description=None, long_description=None):
        """ From the CLI definition parse what are the actual commands and what are flags and/or parameters. """
        cmd_root = Cmd(self.cmd_name)
        cmd_current = cmd_root
        mandatory_parameters = []
        optional_parameters = []
        flags = {}
        flag_mapping = {}

        # parse definition
        for w in filter(None, definition.split(" ")):
            # optional parameter
            if w.startswith('[') and w.endswith(']'):
                opt_w = w[1:-1]  # remove [ ]
                # flag
                if opt_w.startswith('-'):
                    keys, *value = opt_w.split("=", 1)
                    main_key = None
                    for key in keys.split("/"):
                        key = key.lstrip('-').replace("-", "_")
                        if main_key is None:
                            main_key = key
                        flag_mapping[key] = main_key
                    flags[main_key] = bool(value)
                # parameter
                else:
                    if opt_w.endswith('...'):
                        optional_parameters.append((opt_w[:-3], '*'))
                    else:
                        optional_parameters.append((opt_w, 1))
            else:
                cmd_current = cmd_current.new_subcommand(w, wildcard=w[0].isupper())
                if cmd_current.wildcard:
                    mandatory_parameters.append(w)

        cmd_current.activate()

        # Description texts from __doc__.
        if func.__doc__:
            short_description, *long_description = func.__doc__.strip().split('\n', 1)
            long_description = "".join(long_description) or None
            cmd_current['short_description'] = short_description
            cmd_current['long_description'] = long_description
        else:
            if short_description:
                cmd_current['short_description'] = short_description
            if long_description:
                cmd_current['long_description'] = long_description

        cmd_current['name'] = func.__name__
        cmd_current['func'] = func
        cmd_current['usage'] = definition
        cmd_current['params'] = mandatory_parameters
        cmd_current['optional_params'] = optional_parameters
        cmd_current['flags'] = flags
        cmd_current['flag_mapping'] = flag_mapping
        return cmd_root

    def call(self, args=sys.argv[1:]):
        if '--help' in args:
            self.help(args)
            return

        # Remove empty words.
        args = list(filter(None, args))

        if (cmd_info := self.__get_cmd(args)):
            cmd, cmd_args = cmd_info
            cli_args = []
            cli_kwargs = {}

            for a in cmd_args:
                if a.startswith('-'):
                    # argument is a flag
                    kw = a.lstrip('-').split("=")
                    key = cmd['flag_mapping'].get(kw[0].replace("-", "_"))
                    flag_expect_value = cmd['flags'].get(key)
                    if flag_expect_value:
                        cli_kwargs[key] = get_idx(kw, 1)
                    elif flag_expect_value is not None and not flag_expect_value:
                        cli_kwargs[key] = True
                    else:
                        raise UnknownFlag
                else:
                    # just an basic argument, mandatory or optional who knows yet.
                    cli_args.append(a)

            cli_argument_count = len(cmd['params'])
            if len(cli_args) < cli_argument_count:
                raise MissingMandatoryArgument

            for op, count in cmd['optional_params']:
                if count == '*':
                    cli_argument_count = None
                else:
                    cli_argument_count += count

            if cli_argument_count is not None and len(cli_args) > cli_argument_count:
                raise UnknownArgument

            return cmd['func'](*cli_args, **cli_kwargs)
        else:
            raise UnknownCommand

    def help(self, args=sys.argv[1:]):
        if cmd_info := self.__get_cmd(args):
            cmd, _args = cmd_info
            if usage_help := cmd['usage']:
                cmd_root_name = f"{self.cmd_name} " if self.cmd_name else ''
                print(f"Usage: {cmd_root_name}{usage_help}")

            if short_help := cmd['short_description']:
                print(short_help)

            if long_help := cmd['long_description']:
                print(long_help)

            if cmd.subcommands:
                print()
                print('Subcommands:')
                for sub_cmd in cmd.subcommands.values():
                    sub_short_description_text = str(sub_cmd['short_description'] or '')
                    print(f"\t{sub_cmd.name()}\t{sub_short_description_text}")
        else:
            print("no help?")

    def help_all_commands(self, path=None):
        cmd_root_name = f"{self.cmd_name} " if self.cmd_name else ''
        for cmd, cmd_info in self.get_cmds():
            print(f"{cmd_root_name}{cmd_info['usage']}")
            if text := cmd_info['short_description']:
                print(f"\t{text}")

    def call_with_help(self, args=sys.argv[1:]):
        try:
            return self.call(args)
        except MissingMandatoryArgument:
            print("Missing mandatory argument...")
        except UnknownFlag:
            print("Unknown flag passed...")
        except UnknownArgument:
            print("Unknown argument passed...")
        except UnknownCommand:
            print("Unknown command...")
        self.help(args)

    def get_cmds(self):
        yield from self.__get_cmds()

    def __get_cmds(self):
        def __recursive_get_cmd(cmd, path):
            path = f"{path} {cmd.name()}".strip()
            if cmd.active:
                yield path, cmd

            for s in cmd.subcommands.values():
                yield from __recursive_get_cmd(s, path)

        yield from __recursive_get_cmd(self.cmd, "")

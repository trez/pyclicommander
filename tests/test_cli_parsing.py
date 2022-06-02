import unittest
from unittest.mock import patch, call
from pyclicommander import Commander
from pyclicommander.exceptions import UnknownArgument, UnknownFlag, UnknownCommand


class Test_parse_definitions(unittest.TestCase):
    def test_subcommand_no_args(self):
        commander = Commander()

        @commander.cli("mockcmd")
        def subcommand():
            return "CALLED"

        self.assertEqual(commander.call(["mockcmd"]), "CALLED")

    def test_subcommand_multiple_no_args(self):
        commander = Commander()

        @commander.cli("mockcmd apa")
        def subcommand_apa():
            return "APA"

        @commander.cli("mockcmd bepa")
        def subcommand_bepa():
            return "BEPA"

        self.assertEqual(commander.call(["mockcmd", "apa"]), "APA")
        self.assertEqual(commander.call(["mockcmd", "bepa"]), "BEPA")

        with self.assertRaises(UnknownCommand):
            self.assertEqual(commander.call(["mockcmd"]), None)

        with self.assertRaises(UnknownCommand):
            self.assertEqual(commander.call(["mockcmd", "cepa"]), None)

    def test_subcommand_with_mandatory_args(self):
        commander = Commander()

        @commander.cli("mockcmd WORD")
        def subcommand_apa(arg):
            return arg

        # No mandatory argument
        with self.assertRaises(UnknownCommand):
            commander.call(["mockcmd"])

        # Too many arguments
        with self.assertRaises(UnknownArgument):
            commander.call(["mockcmd", "apa", "bepa"])

        # Returns argument
        self.assertEqual(commander.call(["mockcmd", "apa"]), "apa")
        self.assertEqual(commander.call(["mockcmd", "bepa"]), "bepa")

    def test_subcommand_flag_no_value(self):
        commander = Commander()

        @commander.cli("mockcmd [-q]")
        def subcommand_a(q=False):
            return q

        # no flag given, defaults to False
        self.assertEqual(commander.call(["mockcmd"]), False)

        # flag given, return default value True
        self.assertEqual(commander.call(["mockcmd", "-q"]), True)

        # flag given, return default value True and ignore whatever user tries to set.
        self.assertEqual(commander.call(["mockcmd", "-q=Apan"]), True)

        # Unknown flag *r*
        with self.assertRaises(UnknownFlag):
            commander.call(["mockcmd", "-r"])

    def test_subcommand_flag_with_value(self):
        commander = Commander()

        @commander.cli("mockcmd [--user=DATA]")
        def subcommand_a(user=None):
            return user

        # no flag given, defaults to None
        self.assertEqual(commander.call(["mockcmd"]), None)

        # flag given, value apa
        self.assertEqual(commander.call(["mockcmd", "--user=apa"]), "apa")

        # flag given, but no value, return None
        self.assertEqual(commander.call(["mockcmd", "--user"]), None)

    def test_subcommand_double_flags(self):
        commander = Commander()

        @commander.cli("mockcmd [-q/--quiet] [-u/--user=NAME]")
        def subcommand_a(q=False, u=None):
            return q, u

        # no flags given
        self.assertEqual(commander.call(["mockcmd"]), (False, None))

        # short flag used
        self.assertEqual(commander.call(["mockcmd", "-q"]), (True, None))
        self.assertEqual(commander.call(["mockcmd", "-u=apa"]), (False, "apa"))

        # long flag used, True
        self.assertEqual(commander.call(["mockcmd", "--quiet"]), (True, None))
        self.assertEqual(commander.call(["mockcmd", "--user=apa"]), (False, "apa"))

        # both flags used.
        self.assertEqual(commander.call(["mockcmd", "-q", "-u=apa"]), (True, "apa"))
        self.assertEqual(commander.call(["mockcmd", "--quiet", "--user=apa"]), (True, "apa"))

        # order should not matter nor mixing long and short.
        self.assertEqual(commander.call(["mockcmd", "--user=apa", "-q"]), (True, "apa"))

    def test_flag_hyphen(self):
        commander = Commander()

        @commander.cli("mockcmd [--user-data=DATA]")
        def subcommand_a(user_data=[1, 2, 3]):
            return user_data

        self.assertEqual(commander.call(["mockcmd"]), [1, 2, 3])
        self.assertEqual(commander.call(["mockcmd", "--user-data=apa"]), "apa")

    def test_wildcard_command(self):
        commander = Commander()

        @commander.cli("mockcmd PROJECT")
        def subcommand_a(project):
            return "a__" + project

        @commander.cli("mockcmd PROJECT info")
        def subcommand_b(project):
            return "b__" + project

        @commander.cli("mockcmd cmd2")
        def subcommand_c():
            return "apabepa"

        # No mandatory argument
        with self.assertRaises(UnknownCommand):
            commander.call(["mockcmd"])

        self.assertEqual(commander.call(["mockcmd", "apa"]), "a__apa")
        self.assertEqual(commander.call(["mockcmd", "apa", "info"]), "b__apa")
        self.assertEqual(commander.call(["mockcmd", "cmd2"]), "apabepa")

    def test_flags_on_main(self):
        commander = Commander()

        # Base case, only flag on main.
        @commander.cli("[--quiet/-q]")
        def subcommand_a(quiet=False):
            return quiet

        self.assertEqual(commander.call([""]), False)
        self.assertEqual(commander.call(["-q"]), True)

        # Add a defined command.
        @commander.cli("mockcmd")
        def subcommand_b():
            return "apabepa"

        self.assertEqual(commander.call(["mockcmd"]), "apabepa")
        self.assertEqual(commander.call([""]), False)
        self.assertEqual(commander.call(["-q"]), True)

        # Add a wildcard command.
        @commander.cli("CMD apa")
        def subcommand_c(cmd):
            return cmd

        self.assertEqual(commander.call(["lol", "apa"]), "lol")
        self.assertEqual(commander.call([""]), False)
        self.assertEqual(commander.call(["-q"]), True)

    @patch('builtins.print')
    def test_help_printout(self, mock_print):
        # Add a defined command.
        commander = Commander()

        @commander.cli("mockcmd")
        def subcommand_a():
            return "apa"

        @commander.cli("mockcmd bepa")
        def subcommand_b():
            return "bepa"

        commander.call(["mockcmd", "--help"])

        self.assertEqual(mock_print.mock_calls, [
            call('Usage: mockcmd'),
            call(),
            call('Subcommands:'),
            call('\tbepa\t'),
        ])

    @patch('builtins.print')
    def test_help_printout_wildcard(self, mock_print):
        # Add a defined command.
        commander = Commander()

        @commander.cli("mockcmd")
        def subcommand_a():
            return "apa"

        @commander.cli("mockcmd extra")
        def subcommand_e():
            """Normal command."""
            return "extra"

        @commander.cli("mockcmd BEPA")
        def subcommand_b():
            """Wildcard command."""
            return "bepa"

        commander.call(["mockcmd", "--help"])

        self.assertEqual(mock_print.mock_calls, [
            call('Usage: mockcmd'),
            call(),
            call('Subcommands:'),
            call('\textra\tNormal command.'),
            call('\tBEPA\tWildcard command.'),
        ])

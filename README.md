# pyclicommander
Create CLI commands structures by using pyclicommander decorator.

## Installation
```bash
$ python setup.py install
```

## Minimal example:
```python
# save this as test_cli.py
#!/bin/python3
from pyclicommander import Commander
commander = Commander()

@commander.cli("speak WORD")
def speaker(word):
   """ Friendly greater function. """
    print(f"hello {word.upper()}")
    
if __name__ == "__main__":
    commander.call()
```

The decorator creates a mapping for the command *speak* with a mandatory parameter *WORD* to the function *speaker*
that will pass on whatever argument that is given from the command line.

```bash
$ ./test_cli.py speak world
hello WORLD
```

## Usage
### API
| Commander                        | Description                                                                   |
| ---------------------------      | ----------------------------------------------------------------------------- |
| call(cli_path:List[String])      | run command with arguments for cli path. cli_path defaults to sys.argv[1:].   |
|                                  | if --help is in cli_path help() will be called.                               |
|                                  | ex. c.call(["speak", "world"])                                                |
| help(cli_path:List[String])      | print help text for cli path based on function __docstring__.                 |
|                                  | cli_path defaults to sys.argv[1:].                                            |
|                                  | ex. c.call(["speak", "world"])                                                |
| add_cli(path:String, func,       | add extra cli without using decorators.                                       |
|    short_description:String,     |                                                                               |
|    long_description:String)      |                                                                               |

### Definitions
| Feature                | @commander.cli()           | function header      | Note                                               |
| ---------------------- | -------------------------- | -------------------- | -------------------------------------------------- |
| Mandatory parameter(s) | queue accept KEY           | def a(k)             | one mandatory parameter                            |
|                        | queue accept KEY KEY       | def a(k1, k2)        | two mandatory parameters                           |
|                        | queue KEY accept           | def a(k)             | mandatory parameter in cli path                    |
| Optional parameter(s)  | queue accept [KEY]         | def a(k=None)        | one optional parameter                             |
| Optional flags         | queue list [-q]            | def a(q=False)       | when -q is used it is set to True                  |
|                        | queue list [--user=NAME]   | def a(user=None)     |                                                    |
|                        | queue list [-q/--quiet]    | def a(q=False)       | Short and long flags, first flag is used in call.  |
|                        | queue list [--user-data=D] | def a(user_data=[1]) | Hyphens gets replaced by underscore.               |
| List of parameter(s)   | queue accept [KEY...]      | def a(*k)            | zero or more KEYs                                  |
|                        | queue accept KEY [KEY...]  | def a(*k)            | one or more KEYs                                   |
                                               
## Development
### Run tests
```bash
python setup.py test
```

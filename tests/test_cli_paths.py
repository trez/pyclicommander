import unittest
from pyclicommander import Commander
from pyclicommander.exceptions import UnknownCommand, UnknownArgument


class Test_commander_paths(unittest.TestCase):
    def test_base_command(self):
        commander = Commander()

        @commander.cli("mockcmd_before")
        def subcommand_a():
            return "CALLED mockcmd_before"

        @commander.cli("")
        def command():
            return "CALLED MAIN"

        @commander.cli("mockcmd_after")
        def subcommand_b():
            return "CALLED mockcmd_after"

        self.assertEqual(commander.call([]), "CALLED MAIN")
        self.assertEqual(commander.call([""]), "CALLED MAIN")
        self.assertEqual(commander.call(["mockcmd_before"]), "CALLED mockcmd_before")
        self.assertEqual(commander.call(["mockcmd_after"]), "CALLED mockcmd_after")

        # Unknown subcommand *mockcmd_middle*, considred to be argument to the main command.
        with self.assertRaises(UnknownArgument):
            commander.call(["mockcmd_middle"])

    def test_subcommand_add_more_cli(self):
        commander = Commander()

        @commander.cli("mockcmd apa")
        def subcommand_apa():
            return "APA"

        self.assertEqual(commander.call(["mockcmd", "apa"]), "APA")

        with self.assertRaises(UnknownCommand):
            self.assertEqual(commander.call(["mockcmd", "bepa"]), None)

        @commander.cli("mockcmd bepa")
        def subcommand_bepa():
            return "BEPA"

        self.assertEqual(commander.call(["mockcmd", "apa"]), "APA")
        self.assertEqual(commander.call(["mockcmd", "bepa"]), "BEPA")

    def test_subcommand_nested_commands(self):
        commander = Commander()

        @commander.cli("mockcmd queue [-q]")
        def subcommand_ls(q=False):
            if q:
                return "list_queue_silent"
            else:
                return "list_queue"

        @commander.cli("mockcmd queue purge")
        def subcommand_purge():
            return "purge_queue"

        self.assertEqual(commander.call(["mockcmd", "queue"]), "list_queue")
        self.assertEqual(commander.call(["mockcmd", "queue", "-q"]), "list_queue_silent")
        self.assertEqual(commander.call(["mockcmd", "queue", "purge"]), "purge_queue")

        # Unknown subcommand *accept*
        with self.assertRaises(UnknownArgument):
            commander.call(["mockcmd", "queue", "accept"])

        # Unknown subcommand *accept*, flag in the middle
        with self.assertRaises(UnknownArgument):
            commander.call(["mockcmd", "queue", "-q", "accept"])

    def test_add_cli_extra(self):
        commander = Commander()

        @commander.cli("mockcmd_a")
        def subcommand_a():
            return "CALLED a"

        self.assertEqual(commander.call(["mockcmd_a"]), "CALLED a")
        with self.assertRaises(UnknownCommand):
            commander.call(["mockcmd_b"])

        def extra_subcommand_b():
            return "CALLED b"
        commander.add_cli("mockcmd_b", extra_subcommand_b)

        self.assertEqual(commander.call(["mockcmd_a"]), "CALLED a")
        self.assertEqual(commander.call(["mockcmd_b"]), "CALLED b")

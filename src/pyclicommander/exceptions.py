class CommanderError(Exception):
    pass


class MissingMandatoryArgument(CommanderError):
    pass


class UnknownFlag(CommanderError):
    pass


class UnknownArgument(CommanderError):
    pass


class UnknownCommand(CommanderError):
    pass

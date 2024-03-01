import abc

class BaseCommand(abc.ABC):
    command_name = None

    @classmethod
    def add_command(self, subparsers):
        command_parser = subparsers.add_parser(self.command_name)
        command_parser.set_defaults(command_class=self)
        self.add_arguments(command_parser)

    @abc.abstractclassmethod
    def add_arguments(self, parser):
        pass

    def __init__(self, arguments):
        self.arguments = arguments

    @abc.abstractmethod
    def __call__(self):
        pass

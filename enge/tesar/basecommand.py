import abc
import logging

LOGGER = logging.getLogger()

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
        LOGGER.debug(f'Command "{self.command_name}" is being run with arguments: {arguments}')
        self.args = arguments

    @abc.abstractmethod
    def __call__(self):
        pass

from ..basecommand import BaseCommand

class DispatchCommand(BaseCommand):
    command_name = 'dispatch'

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument('message')

    def __call__(self):
        print(self.arguments.message)

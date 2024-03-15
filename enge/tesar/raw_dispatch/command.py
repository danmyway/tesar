from ..basecommand import BaseCommand
from ..tfrequest import TFRequest

class RawDispatchCommand(BaseCommand):
    command_name = 'raw_dispatch'

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument('--git_url', default=None)
        parser.add_argument('--git_branch', default=None) # use commit id as default
        parser.add_argument('--git_path', default=None)
        parser.add_argument('--plan_name', default=None)
        parser.add_argument('--plan_filter', default=None)
        parser.add_argument('--test_filter', default=None)

    def __call__(self):
        tf_kwargs = {}
        for arg in ('git_url', 'git_branch', 'git_path', 'plan_name', 'plan_filter', 'test_filter'):
            tf_kwargs[arg] = getattr(self.args, arg)
        request = TFRequest(**tf_kwargs)
        print(self.args)

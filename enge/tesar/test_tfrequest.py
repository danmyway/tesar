import unittest

from .tfrequest import TFRequest

class TestProperties(unittest.TestCase):
    def setUp(self):
        self.r = TFRequest(git_url='foo')

    def test_init(self):
        self.assertEqual(self.r.git_url, 'foo')

    @unittest.skip
    def test_setter(self):
        pass

    @unittest.skip
    def test_deleter(self):
        pass


class TestEqual(unittest.TestCase):
    full_kwargs_set = {
        'git_url' : 'hello',
        'git_branch' : 'hia',
        'git_path' : 'ciao',
        'plan_name' : 'hallo',
        'plan_filter' : 'привіт',
        'test_filter' : 'ahoj',
        'environments' : 'dobrodošli',
    }

    def test_empty_equals(self):
        self.assertEqual(
            TFRequest(),
            TFRequest()
        )

    def test_various_equals(self):
        kwargs_sets = (
            {'git_url':'foo'},
            self.full_kwargs_set,
        )
        for kwargs_set in kwargs_sets:
            with self.subTest(kwargs_set=kwargs_set):
                original = TFRequest(**kwargs_set)
                self.assertEqual(
                    original,
                    original.copy()
                )

    def test_various_nonequals(self):
        kwargs_set = self.full_kwargs_set
        reference = TFRequest(**kwargs_set)
        diff_sets = (
            {'git_url': ''},
            {'plan_name': None, 'test_filter': None},
        )
        for diff_set in diff_sets:
            with self.subTest(diff_set=diff_set):
                new_kwargs = kwargs_set.copy()
                new_kwargs.update(diff_set)
                self.assertNotEqual(
                    reference,
                    TFRequest(new_kwargs)
                )

    def test_different_request_id(self):
        self.assertNotEqual(
            TFRequest('one', **self.full_kwargs_set),
            TFRequest('two', **self.full_kwargs_set)
        )


class TestCopy(unittest.TestCase):
    def setUp(self):
        self.r = TFRequest(git_url='foo', git_branch='bar')

    def test_copy_simple(self):
        self.assertEqual(
            self.r,
            self.r.copy(),
        )

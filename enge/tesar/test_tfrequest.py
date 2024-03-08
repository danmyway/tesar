import unittest

from .tfrequest import TFRequest, FrozenException

FULL_KWARGS_SET = {
    'git_url' : 'hello',
    'git_branch' : 'hia',
    'git_path' : 'ciao',
    'plan_name' : 'hallo',
    'plan_filter' : 'привіт',
    'test_filter' : 'ahoj',
    'environments' : 'dobrodošli',
}


class TestProperties(unittest.TestCase):
    def setUp(self):
        self.r = TFRequest(git_url='foo')

    def test_init(self):
        self.assertFalse(self.r.frozen)
        self.assertEqual(self.r.git_url, 'foo')

    def test_setter(self):
        self.r.git_branch = 'baz'
        self.assertEqual(self.r.git_branch, 'baz')

    @unittest.skip
    def test_deleter(self):
        pass


class TestFrozenProperties(unittest.TestCase):
    def setUp(self):
        self.r = TFRequest('hello')

    def test_init(self):
        self.assertTrue(self.r.frozen)

    def test_setter(self):
        with self.assertRaises(FrozenException):
            self.r.git_branch = 'baz'

    @unittest.skip
    def test_deleter(self):
        pass

    def test_init_with_other_values(self):
        for key, value in FULL_KWARGS_SET.items():
            with self.subTest(kwarg=(key, value)):
                with self.assertRaises(FrozenException):
                    TFRequest('req_id', **dict([(key, value)]))


class TestEqual(unittest.TestCase):
    def test_empty_equals(self):
        self.assertEqual(
            TFRequest(),
            TFRequest()
        )

    def test_various_equals(self):
        kwargs_sets = (
            {'git_url':'foo'},
            FULL_KWARGS_SET.copy(),
        )
        for kwargs_set in kwargs_sets:
            with self.subTest(kwargs_set=kwargs_set):
                original = TFRequest(**kwargs_set)
                self.assertEqual(
                    original,
                    original.copy()
                )

    def test_various_nonequals(self):
        kwargs_set = FULL_KWARGS_SET.copy()
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
            TFRequest('one'),
            TFRequest('two')
        )


class TestCopy(unittest.TestCase):
    def setUp(self):
        self.r = TFRequest(git_url='foo', git_branch='bar')

    def test_copy_simple(self):
        self.assertEqual(
            self.r,
            self.r.copy(),
        )

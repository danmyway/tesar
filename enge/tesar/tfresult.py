from collections import OrderedDict

RESULTS = OrderedDict((
    (None, 'No valid result is available.'),
    ('PASS', 'The test has passed.'),
    ('FAIL', 'The test has failed.'),
    ('ERROR', 'There was an error during the execution.'),
))

class TFResult():
    def __init__(self, request, architecture, testplan, test, result, logs):
        self.request = request
        self.architecture = architecture
        self.testplan = testplan
        self.test = test
        self.result = result
        self.logs = logs

    def __str__(self):
        return f'<TFResult>(request_id={self.request.id}, arch={self.architecture}, testplan={self.testplan}, test={self.test}, result={self.result})'


class TFResultsList(list):
    def by_key(self, key_func):
        """
        Group tfresults based on result of key_func.

        :param key_func:
        :type key_func: callable
        :return:
        :rtype dict:
        """
        result = {}
        for tfresult in self:
            key = key_func(tfresult)
            try:
                result[key].append(tfresult)
            except KeyError:
                result[key] = TFResultsList([tfresult])
        return result

    @property
    def result(self):
        """Return highest result present in the caseRunConfigurations"""
        results = { result:i for i, result in enumerate(RESULTS) }
        return list(RESULTS)[max([results[tfresult.result.result] for tfresult in self])]

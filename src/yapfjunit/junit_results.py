import abc
import os

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import SubElement


class JUnitReport(object):
    """Representation of a test run."""

    def __init__(self, failure_count, error_count, results):
        """
        Create a JUnitRun object.

        :param failure_count: number of failure encountered.
        :param error_count:  number of errors encountered.
        :param results: list of results.
        """
        self._failure_count = failure_count
        self._error_count = error_count
        self._results = results

    def to_xml(self):
        """
        Create xml object representing results.

        :return: xml object of results.
        """
        root = Element('testsuites')
        test_suite = SubElement(
            root,
            'testsuite',
            errors=str(self._error_count),
            failures=str(self._failure_count),
            name='yapf',
            tests=str(len(self._results)))

        for result in self._results:
            result.to_xml(test_suite)

        return ElementTree(root)


class JUnitResult(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, filename, runtime):
        """
        Create a JUnit Result.

        :param filename: filename of test.
        :param runtime: runtime of test.
        """
        self._filename = filename
        self._runtime = runtime

    def suite(self):
        """
        Get the suite name of the test.

        :return: suite name of test.
        """
        return os.path.dirname(self._filename)

    def name(self):
        """
        Get the name of the test.

        :return: name of test.
        """
        return os.path.basename(self._filename)

    def get_formatted_runtime(self):
        """
        Get a string version of the runtime.

        :return: Runtime of test.
        """
        return str(self._runtime)

    def _get_testcase_xml(self, parent):
        """
        Return the xml element for the test case.

        :param parent: Parent element.
        :return: element representing this testcase.
        """
        return SubElement(
            parent,
            'testcase',
            classname=self.suite(),
            name=self.name(),
            time=str(self.get_formatted_runtime()))

    def to_xml(self, parent):
        """
        Create xml for this test case.

        :param parent: parent element.
        """
        self._get_testcase_xml(parent)


class JUnitError(JUnitResult):
    """JUnit Error Result."""

    def __init__(self, filename, text, runtime):
        """
        Create a JUnitError object.

        :param filename: filename of test being run.
        :param text: test of error message
        :param runtime: runtime of test.
        """
        self._text = text
        super(JUnitError, self).__init__(filename, runtime)

    def to_xml(self, parent):
        """
        Return xml for this test result.
        :param parent: Parent xml element.
        """
        testcase = self._get_testcase_xml(parent)
        SubElement(
            testcase, 'error', type='Could not run yapf').text = self._text


class JUnitFailure(JUnitResult):
    """JUnit Failure Result."""

    def __init__(self, filename, text, runtime):
        """
        Create a JUnitFailure object.

        :param filename: filename of test being run.
        :param text: test of error message
        :param runtime: runtime of test.
        """
        self._text = text
        super(JUnitFailure, self).__init__(filename, runtime)

    def to_xml(self, parent):
        """
        Return xml for this test result.
        :param parent: Parent xml element.
        """
        testcase = self._get_testcase_xml(parent)
        SubElement(testcase, 'failure', type='yapf failure').text = self._text

from yapfjunit.junit_results import JUnitReport
from yapfjunit.junit_results import JUnitResult
from yapfjunit.junit_results import JUnitError
from yapfjunit.junit_results import JUnitFailure


def test_junit_report():
    results = [
        JUnitResult('dir0/result0', 1.23),
        JUnitError('dir0/result1', 'error test 0', 2.24),
        JUnitResult('dir1/result1', 0.756),
        JUnitError('dir1/result2', 'error test 1', 3.45),
        JUnitFailure('dir2/result0', 'a failure', 0.01),
    ]
    expected_error_count = 2
    expected_failure_count = 1

    report = JUnitReport(expected_failure_count, expected_error_count, results)

    xml = report.to_xml()
    root = xml.getroot()

    assert root.tag == 'testsuites'

    for child in root:
        assert child.tag == 'testsuite'
        assert child.get('errors') == str(expected_error_count)
        assert child.get('failures') == str(expected_failure_count)
        assert child.get('tests') == str(len(results))
        assert len(child) == len(results)

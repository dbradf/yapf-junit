#!/usr/bin/env python

import datetime
import os
import sys
import xml.etree.ElementTree as ET

import click
from yapf.yapflib.yapf_api import FormatFile
from lib2to3.pgen2.parse import ParseError


def create_xml_results(failed_tests, err_count, results):
    """
    Create junit xml for the test results.

    :param failed_tests: Number of tests that failed.
    :param err_count: Number of tests that hit errors.
    :param results: List of test results.
    :return: junit xml results.
    """
    root = ET.Element('testsuites')
    test_suite = ET.SubElement(root, 'testsuite', errors=err_count,
                               failures=failed_tests, name='yapf', tests=len(results))
    for result in results:
        result.to_xml(test_suite)

    tree = ET.ElementTree(root)
    return tree

    # return f"""<?xml version="1.0" ?>
    # <testsuites>
    #     <testsuite errors="{err_count}" failures="{failed_tests}" name="yapf" tests="{len(results)}">
    #         {test_case_output}
    #     </testsuite>
    # </testsuites>""testsuites"


class YapfResult:
    """
    Results of a yapf run.
    """
    def __init__(self, filename, diff, needs_change, runtime):
        """
        Create a YapfResult.

        :param filename: file being analyzed.
        :param diff: changes found.
        :param needs_change: did the file fail yapf.
        :param runtime: how long the analysis ran.
        """
        self._filename = filename
        self._diff = diff
        self._needs_change = needs_change
        self._runtime = runtime.total_seconds()

    def suite(self):
        """Name of suite (directory analyzed)."""
        return os.path.dirname(self._filename)

    def name(self):
        """Name of test (filename)."""
        return os.path.basename(self._filename)

    def to_xml(self, parent):
        """
        Convert yapf result to junit xml.
        """
        test = ET.SubElement(parent, 'testcase', classname=self.suite(), name=self.name(), time=self._runtime)
        ET.SubElement(test, 'system-err').text = self._diff


def find_files(root_dir, extension):
    """
    Find files in the root directory with the provided extension.

    :param root_dir: Directory to search.
    :param extension: extension to search for.
    :return: List of files with the given extension.
    """
    target_files = []
    files = os.listdir(root_dir)
    for f in files:
        path = os.path.join(root_dir, f)
        if os.path.isdir(path):
            target_files += find_files(path, extension)
        elif f.endswith(extension):
            target_files.append(path)

    return target_files


@click.command()
@click.option('--dir', required=True, help='Directory to search.')
@click.option('--out-file', required=True, help='File to write results to.')
def yapf_junit(dir, out_file):
    files_to_run = find_files(dir, '.py')

    results = []
    failure_count = 0
    err_count = 0
    for f in files_to_run:
        start_time = datetime.datetime.now()
        try:
            diff, encoding, needs_change = FormatFile(f, print_diff=True)
            if needs_change:
                failure_count += 1
        except ParseError as err:
            diff = str(err)
            needs_change = True
            err_count += 1

        end_time = datetime.datetime.now()
        results.append(YapfResult(f, diff, needs_change, end_time - start_time))

    xml_data = create_xml_results(failure_count, err_count, results)
    xml_data.write(out_file)

    # with open(out_file, 'w') as fp:
    #     fp.write(xml_data)

    if failure_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    yapf_junit()

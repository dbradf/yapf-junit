#!/usr/bin/env python

import datetime
import os
import sys

import click
from yapf.yapflib.yapf_api import FormatFile
from lib2to3.pgen2.parse import ParseError

from yapfjunit.junit_results import JUnitResult
from yapfjunit.junit_results import JUnitError
from yapfjunit.junit_results import JUnitFailure
from yapfjunit.junit_results import JUnitReport


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


def run_yapf(target_file, failure_count, error_count, yapf_config):
    """
    Run yapf on the target file.

    :param target_file: file to run against.
    :param failure_count: number of failures encountered.
    :param error_count: number of errors encountered.
    :param yapf_config: yapf config to use.
    :return: results of yapf run.
    """
    start_time = datetime.datetime.now()
    try:
        diff, encoding, needs_change = FormatFile(
            target_file, print_diff=True, style_config=yapf_config)
        if needs_change:
            end_time = datetime.datetime.now()
            failure_count += 1
            return JUnitFailure(target_file, diff, end_time - start_time)
    except ParseError as err:
        end_time = datetime.datetime.now()
        error_count += 1
        return JUnitError(target_file, str(err), end_time - start_time)

    end_time = datetime.datetime.now()
    return JUnitResult(target_file, end_time - start_time)


@click.command()
@click.option('--target-dir', required=True, help='Directory to search.')
@click.option('--out-file', required=True, help='File to write results to.')
@click.option('--yapf-config', help='Yapf config file to use.')
def yapf_junit(target_dir, out_file, yapf_config):
    files_to_run = find_files(target_dir, '.py')

    failure_count = 0
    err_count = 0
    results = [
        run_yapf(target_file, failure_count, err_count, yapf_config)
        for target_file in files_to_run
    ]

    report = JUnitReport(failure_count, err_count, results)
    report.to_xml().write(out_file)

    if (failure_count + err_count) > 0:
        sys.exit(1)


if __name__ == '__main__':
    yapf_junit()

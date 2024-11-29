"""
Unit tests for command-line options
"""
import pytest

from tesar.dispatch.__init__ import get_arguments


def test_cmd_args_are_appended():
    """Unit test covering tesar report -c test1 -c test2 behavior for results aggregation"""
    # Make sure -c are treated as list
    args = get_arguments(
        [
            "report",
            "-c",
            "http://artifacts.osci.redhat.com/testing-farm/909143cf-89ca-4d62-8f81-959bf8ab4d03/",
            "-c",
            "http://artifacts.osci.redhat.com/testing-farm/14612a82-002d-4a8d-a5c4-613a0a75efeb/",
        ]
    )
    assert len(args.cmd) == 2
    # Make official the behavior that -c test1 test2 test3 is not supported anymore
    with pytest.raises(SystemExit):
        get_arguments(
            [
                "report",
                "-c",
                "http://artifacts.osci.redhat.com/testing-farm/909143cf-89ca-4d62-8f81-959bf8ab4d03/",
                "http://artifacts.osci.redhat.com/testing-farm/14612a82-002d-4a8d-a5c4-613a0a75efeb/",
            ]
        )
        get_arguments(
            [
                "report",
                "-c",
                "http://artifacts.osci.redhat.com/testing-farm/909143cf-89ca-4d62-8f81-959bf8ab4d03/",
                "http://artifacts.osci.redhat.com/testing-farm/14612a82-002d-4a8d-a5c4-613a0a75efeb/",
            ]
        )


def test_git_arg_four_nargs():
    """Unit test covering tesar test -g accepting four arguments."""
    # Pass all four arguments to the --git arg
    args = get_arguments(
        [
            "test",
            "copr",
            "c2r",
            "-r",
            "pr123",
            "-p",
            "mock_plan",
            "-g",
            "github",
            "oamg",
            "convert2rhel",
            "devel",
        ]
    )
    assert len(args.git) == 4
    # Pass less than 4 arguments
    with pytest.raises(SystemExit):
        get_arguments(
            [
                "test",
                "copr",
                "c2r",
                "-r",
                "pr123",
                "-p",
                "mock_plan",
                "-g",
                "github",
                "oamg",
                "devel",
            ]
        )

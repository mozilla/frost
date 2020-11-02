import os
import sys
import glob

import click
import pytest


FROST_PARENT_DIRECTORY = os.path.dirname(os.path.dirname(__file__))


def switch_to_frost_parent_directory():
    """
    Changes to the frost CLI parent directory

    This shouldn't be necessary once tests move to frost/
    """
    # look up frost/.. to get the repo root dir
    os.chdir(FROST_PARENT_DIRECTORY)


@click.group()
@click.version_option()
def cli():
    """
    FiRefox Operations Security Testing API clients and tests
    """
    pass


@cli.command(
    "list", context_settings=dict(ignore_unknown_options=True,),
)
def list_tests():
    """
    Lists available test filenames packaged with frost.
    """
    switch_to_frost_parent_directory()
    sys.stdout.writelines(
        f"{test_file_path}\n"
        for test_file_path in glob.glob("./**/test*.py", recursive=True)
        if not ("/venv" in test_file_path or "/build" in test_file_path)
    )


@cli.command(
    "test", context_settings=dict(ignore_unknown_options=True,),
)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run_pytest(ctx, pytest_args):
    """
    Run pytest tests passing all trailing args to pytest.

    Adds the pytest args:

    -s to disable capturing stdout https://docs.pytest.org/en/latest/capture.html

    and frost specific args:

    --debug-calls to print AWS API calls
    --ignore-glob='*.py' to require explicit test specification
    """
    switch_to_frost_parent_directory()
    sys.exit(
        pytest.main(["-s", "--debug-calls", "--ignore-glob='*.py'"] + list(pytest_args))
    )


if __name__ == "__main__":
    cli()

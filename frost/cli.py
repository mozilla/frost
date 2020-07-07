import sys

import click
import pytest


@click.group()
@click.version_option()
def cli():
    """
    FiRefox Operations Security Testing API clients and tests
    """
    pass


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def test(ctx, pytest_args):
    """
    Run pytest tests passing all trailing args to pytest.
    """
    pytest.main(list(pytest_args))


if __name__ == "__main__":
    cli()

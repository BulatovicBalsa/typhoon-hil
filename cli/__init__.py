import click
from myvalidator.validations import validate
from myvalidator.validations_collector import validators


@click.group()
@click.option('--debug', default=False, is_flag=True,
              help="Debug/trace output.")
@click.pass_context
def cli(ctx, debug):
    ctx.obj = {'debug': debug}


@cli.command()
@click.argument('json_path', type=click.Path(), required=True)
@click.argument('tse_path', type=click.Path(), required=True)
@click.argument('validator_name', required=True)
@click.pass_context
def validate_graph(ctx, json_path, tse_path, validator_name):
    """Checks if the given graph is valid."""
    validate(json_path, tse_path, validator_name)


@cli.command()
@click.pass_context
def validation_list(ctx):
    """Lists all currently available validations"""
    for desc in validators.values():
        click.echo("{} -> {}".format(desc.name, desc.desc))


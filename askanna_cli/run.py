import click
import pkg_resources


HELP = """
This command will allow you to perform a run on a remote
location for the particular project.
"""

SHORT_HELP = "Execute run of deployed AskAnna project"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument("kernel", required=False, default="default")
def cli(kernel):

    kernels = {}

    # inspect the askanna_kernel entry_point for existing kernels
    for entry_point in pkg_resources.iter_entry_points('askanna_kernels'):
        kernels[entry_point.name] = entry_point.load()

    if kernel != "default":

        # retrieve the passed on kernel, and execute
        try:
            torun = kernels[kernel]
        except KeyError:
            click.echo("No Kernel with name {kernel}".format(kernel=kernel))
            return 0

        torun.run_kernel()

    else:

        if kernels:
            click.echo("The following kernels are available:")
            for key, value in kernels.items():
                click.echo("\t{key}".format(key=key))

            click.echo("\nRun with:\n")
            click.echo("\taskanna run [kernel]")

        click.echo("No kernels yet registered in the system!")
        click.echo("Use the createproject to create some!")

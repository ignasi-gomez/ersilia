import click
from click.testing import CliRunner

from . import ersilia_cli
from .. import echo

from ...utils.logging import logger

#Imports for the pipeline
from ersilia.cli.commands.fetch import fetch_cmd
from ersilia.cli.commands.serve import serve_cmd
from ersilia.cli.commands.example import example_cmd
from ersilia.cli.commands.run import run_cmd
from ersilia.cli.commands.close import close_cmd

#Imports to get system information
import subprocess

def performance_cmd():
    """
    Generates a Hardware performance report on a selected model.

    The report includes the following information:
    · Hardware configuration.
    · Model selected for evaluation.
    · CPU ussage: Including MAX, MIN and AVG CPU Load during process execution.
    · Memory ussage: Same as with CPU, measure memory. 
    · Duration of test: Same as with CPU, measure clock time in seconds.
    · Disk I/O ussage: We compute disk ussage at the start of the test. Then compute the
        lambda (increment) in disk ussage. We return the maximum increment. Ussage is measured
        in CPU time used for disk I/O operations.
    · Network ussage: Similar to disk, uses a lambda. Compute megabytes received.

    Returns
    -------
    function
        The performance command function to be used by the CLI and for testing in the pytest.

    Examples
    --------
    .. code-block:: console

    Run a performance test for a specific model ID and stores the results in a report file:
    $ ersilia performance <model_id> --file_name <file_path>
    """

    def __run_cli_tool(cli_runner,cli_function,cli_params):
        """
        Wrapper to run another cli tool
        """
        try:
            result = cli_runner.invoke(cli_function, cli_params)
        except Exception as e:
            click.secho(f"⚠️ {str(e)} ⚠️")
        return result
        
    # Example usage: ersilia performance eos4e40
    @ersilia_cli.command(help="""Generates a Hardware performance report on a selected model.
        e.g., 
        ersilia performance eos4e40 --file_name report.txt""")
    @click.argument("model",
        type=click.STRING,
        required=True,)
    @click.option("--file_name", "-f", default="report.txt", type=click.STRING)
    @click.option("--sleep_time", "-s", default=10, type=click.INT)

    def performance(model, file_name="report.txt", sleep_time=10):
        #Start performance metrics process
        proc = subprocess.Popen(f"python ./ersilia/cli/commands/utils/resource_monitor.py {sleep_time} {model} {file_name}", shell=True)
        result = 0
        #For enacting othe CLI functionalities.
        runner = CliRunner()
        #Fetch model
        result = __run_cli_tool(runner,fetch_cmd(),[model])
        if result.exit_code != 0 :
            click.secho(f"⛔️ Error when fetching model: {model} ⛔️",fg="red")
            return result
        #Serve model
        result = __run_cli_tool(runner,serve_cmd(),[model])
        if result.exit_code != 0 :
            click.secho(f"⛔️ Error when serving model: {model} ⛔️",fg="red")
            return result
        #Generate example inputs for model
        result = __run_cli_tool(runner,example_cmd(),["-n5", "-fmy_input.csv"])
        if result.exit_code != 0 :
            click.secho(f"⛔️ Error when generating samples for the model: {model} ⛔️",fg="red")
            return result
        #Run model
        result = __run_cli_tool(runner,run_cmd(),["-imy_input.csv", "-omy_output.csv"])
        if result.exit_code != 0 :
            click.secho(f"⛔️ Error when running model: {model} ⛔️",fg="red")
            return result
        #Close model
        result = __run_cli_tool(runner,close_cmd(),[])
        if result.exit_code != 0 :
            click.secho(f"⛔️ Error when closing model: {model} ⛔️",fg="red")
            return result
        #Stop performance metrics process so report is generated
        proc.terminate()
        return result

    return performance


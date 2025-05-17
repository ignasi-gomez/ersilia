import pytest

from click.testing import CliRunner

from ersilia.cli.commands.performance import performance_cmd
from ersilia.core.model import ErsiliaModel
from ersilia.core.session import Session
from unittest.mock import patch, AsyncMock

MODEL_ID = "eos4e40"
MODEL_ID_BAD = "feos4e40"

def test_performance_cmd_ok():
    runner = CliRunner()
    result = runner.invoke(performance_cmd(), [MODEL_ID])
    print(result)
    assert result.exit_code == 0

def test_performance_cmd_bad_model_id():
    runner = CliRunner()
    result = runner.invoke(performance_cmd(), [MODEL_ID_BAD])
    print(result)
    assert result.exit_code != 0

if __name__ == '__main__':
    test_performance_cmd_ok()
    #test_performance_cmd_bad_model_id()
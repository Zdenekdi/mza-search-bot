import pytest
from click.testing import CliRunner
from mza_search.cli import cli
from mza_search.client import MZAClient

def test_cli_help():
    """Smoke test pro ověření spuštění CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    # Ověříme, že návratový kód je 0 (úspěch)
    assert result.exit_code == 0
    # Ověříme, že nápověda obsahuje klíčová slova z aplikace
    assert "MZA Parish Register Search & Scan Tool" in result.output
    # Ověříme, že jsou vypsány hlavní příkazy
    assert "search" in result.output
    assert "lookup" in result.output
    assert "download" in result.output

def test_client_init():
    """Smoke test pro ověření inicializace HTTP klienta."""
    client = MZAClient()

    # Ověříme, že se vytvořila instance klienta s potřebnou konfigurací
    assert client.client is not None
    assert 'User-Agent' in client.client.headers
    assert client.BASE_URL == "https://www.mza.cz/actapublica/matrika/hledani"

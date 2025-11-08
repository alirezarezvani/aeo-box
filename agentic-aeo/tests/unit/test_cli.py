"""
Unit Tests for CLI Commands

Tests CLI command structure, options, and basic functionality.
"""

import pytest
from click.testing import CliRunner
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cli.main import cli
from cli.commands.campaign import campaign
from cli.commands.compete import compete
from cli.commands.monitor import monitor


class TestCLIMain:
    """Test main CLI entry point."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test CLI displays help."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'AEO Multi-Agent System' in result.output
        assert 'campaign' in result.output
        assert 'compete' in result.output
        assert 'monitor' in result.output

    def test_cli_version(self, runner):
        """Test CLI displays version."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.5.0' in result.output


class TestCampaignCommand:
    """Test campaign command."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_campaign_help(self, runner):
        """Test campaign command help."""
        result = runner.invoke(cli, ['campaign', '--help'])
        assert result.exit_code == 0
        assert 'Run complete AEO campaign' in result.output
        assert '--mode' in result.output
        assert '--level' in result.output

    def test_campaign_requires_url(self, runner):
        """Test campaign requires URL argument."""
        result = runner.invoke(cli, ['campaign'])
        assert result.exit_code != 0
        assert 'Missing argument' in result.output or 'Error' in result.output

    def test_campaign_validates_mode(self, runner):
        """Test campaign validates mode option."""
        result = runner.invoke(cli, ['campaign', 'https://example.com', '--mode', 'invalid'])
        assert result.exit_code != 0


class TestCompeteCommand:
    """Test compete command."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_compete_help(self, runner):
        """Test compete command help."""
        result = runner.invoke(cli, ['compete', '--help'])
        assert result.exit_code == 0
        assert 'competitive AEO analysis' in result.output or 'Competitive' in result.output
        assert '--region' in result.output

    def test_compete_requires_topic(self, runner):
        """Test compete requires topic argument."""
        result = runner.invoke(cli, ['compete'])
        assert result.exit_code != 0
        assert 'Missing argument' in result.output or 'Error' in result.output

    def test_compete_requires_competitors(self, runner):
        """Test compete requires competitor URLs."""
        result = runner.invoke(cli, ['compete', 'test-topic'])
        assert result.exit_code != 0


class TestMonitorCommand:
    """Test monitor command."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_monitor_help(self, runner):
        """Test monitor command help."""
        result = runner.invoke(cli, ['monitor', '--help'])
        assert result.exit_code == 0
        assert 'citation monitoring' in result.output or 'Monitor' in result.output
        assert '--duration' in result.output

    def test_monitor_requires_url(self, runner):
        """Test monitor requires URL argument."""
        result = runner.invoke(cli, ['monitor'])
        assert result.exit_code != 0
        assert 'Missing argument' in result.output or 'Error' in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

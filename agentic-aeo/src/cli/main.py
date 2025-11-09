"""
AEO Multi-Agent CLI

Command-line interface for Answer Engine Optimization workflows.
"""

import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands.campaign import campaign
from cli.commands.compete import compete
from cli.commands.monitor import monitor


@click.group()
@click.version_option(version="1.5.0", prog_name="aeo-agent")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--data-dir', type=click.Path(), default=".aeo-agent-data",
              help='Data directory for campaigns and results')
@click.pass_context
def cli(ctx, verbose, data_dir):
    """
    AEO Multi-Agent System - Answer Engine Optimization Automation

    Optimize your content to be cited by AI language models (ChatGPT, Perplexity,
    Claude, Gemini, Mistral) using automated multi-agent workflows.

    \b
    ⚠️  PROGRESS LIMITATION (v1.5):
    CLI does NOT show real-time progress during campaign execution. Campaigns
    run silently and may take 15-90 minutes depending on mode. Use --verbose
    for additional logging. Real-time progress bars planned for v1.6.

    \b
    Available Commands:
      campaign    Run complete AEO campaign
      compete     Competitive AEO analysis
      monitor     Citation monitoring

    \b
    Examples:
      # Run complete campaign
      aeo-agent campaign https://example.com/article

      # Competitive analysis
      aeo-agent compete "topic" https://comp1.com https://comp2.com

      # Start monitoring
      aeo-agent monitor https://example.com/article --duration 90
    """
    # Ensure data directory exists
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['data_dir'] = str(data_path)


# Register commands
cli.add_command(campaign)
cli.add_command(compete)
cli.add_command(monitor)


if __name__ == '__main__':
    cli()

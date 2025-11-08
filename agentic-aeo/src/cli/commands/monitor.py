"""
Monitor Command - Citation Monitoring

Implements the /aeo-monitor CLI command.
"""

import click
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.orchestrator_agent import OrchestratorAgent
from agents.auditor_agent import AuditorAgent
from agents.citation_tracker_agent import CitationTrackerAgent
from agents.reporter_agent import ReporterAgent
from workflows.monitoring_workflow import MonitoringWorkflow
from communication.protocol import AgentType


@click.command()
@click.argument('url')
@click.option('--duration', type=int, default=90,
              help='Monitoring duration in days (1-365)')
@click.option('--queries', multiple=True,
              help='Specific queries to track (can specify multiple)')
@click.option('--no-alerts', is_flag=True,
              help='Disable change alerts')
@click.option('--no-weekly', is_flag=True,
              help='Disable weekly reports')
@click.option('--output', type=click.Path(), help='Output file for initial report')
@click.pass_context
def monitor(ctx, url, duration, queries, no_alerts, no_weekly, output):
    """
    Start citation monitoring for a URL.

    Sets up continuous monitoring to track how often the content is cited
    by AI language models over time.

    \b
    URL: The URL to monitor

    \b
    Examples:
      # Monitor for 90 days (default)
      aeo-agent monitor https://example.com/article

      # Monitor for 30 days with specific queries
      aeo-agent monitor https://example.com/article --duration 30 --queries "topic 1" --queries "topic 2"

      # Monitor without alerts
      aeo-agent monitor https://example.com/article --duration 60 --no-alerts --no-weekly
    """
    verbose = ctx.obj.get('verbose', False)
    data_dir = ctx.obj.get('data_dir', '.aeo-agent-data')

    # Print monitoring start info
    click.echo(f"\n{'='*60}")
    click.echo(f"  Citation Monitoring Setup")
    click.echo(f"{'='*60}\n")
    click.echo(f"URL:              {url}")
    click.echo(f"Duration:         {duration} days")
    if queries:
        click.echo(f"Target Queries:   {', '.join(queries)}")
    click.echo(f"Alerts:           {'No' if no_alerts else 'Yes'}")
    click.echo(f"Weekly Reports:   {'No' if no_weekly else 'Yes'}")
    click.echo(f"Data Directory:   {data_dir}\n")

    # Initialize workflow
    workflow = MonitoringWorkflow()

    # Validate input
    is_valid, error = workflow.validate_input(url, duration)
    if not is_valid:
        click.echo(f"❌ Error: {error}", err=True)
        sys.exit(1)

    # Initialize orchestrator with required agents
    click.echo("Initializing agents...")
    orchestrator = OrchestratorAgent()

    try:
        # Register required agents
        orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())
        orchestrator.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(
            data_path=f"{data_dir}/citations.csv"
        ))
        orchestrator.register_agent(AgentType.REPORTER, ReporterAgent())

        click.echo(f"✓ Registered {len(orchestrator.agents)} agents\n")

        # Decompose workflow
        if verbose:
            click.echo("Decomposing workflow into tasks...")

        tasks = workflow.decompose(
            url=url,
            duration_days=duration,
            queries=list(queries) if queries else None,
            alert_on_changes=not no_alerts,
            weekly_reports=not no_weekly
        )

        if verbose:
            click.echo(f"✓ Created {len(tasks)} tasks\n")

        # Execute workflow
        click.echo("Setting up monitoring...")
        click.echo("Running baseline audit...\n")

        # Run async execution
        manifest = asyncio.run(orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": url,
                "duration_days": duration,
                "queries": list(queries) if queries else None,
                "alert_on_changes": not no_alerts,
                "weekly_reports": not no_weekly
            }
        ))

        # Check execution status
        if manifest.workflow_state.status.value == "completed":
            click.echo("✅ Monitoring setup completed successfully!\n")

            # Generate executive summary
            results_dict = {
                result.task_id: result
                for result in manifest.task_results
            }

            summary = workflow.create_executive_summary(
                results_dict,
                url,
                duration
            )

            # Display summary
            click.echo("="*60)
            click.echo("  MONITORING SETUP SUMMARY")
            click.echo("="*60 + "\n")
            click.echo(summary.get("executive_summary", "No summary available"))
            click.echo()

            # Display baseline metrics
            baseline = summary.get("baseline_metrics", {})
            if baseline.get("baseline_aeo_score") is not None:
                click.echo("="*60)
                click.echo("  BASELINE METRICS")
                click.echo("="*60)
                click.echo(f"AEO Score:        {baseline['baseline_aeo_score']}/100")
                if baseline.get("baseline_eeat_score"):
                    click.echo(f"E-E-A-T Score:    {baseline['baseline_eeat_score']}/100")
                if baseline.get("baseline_structure_score"):
                    click.echo(f"Structure Score:  {baseline['baseline_structure_score']}/100")
                if baseline.get("baseline_citations_count"):
                    click.echo(f"Current Citations: {baseline['baseline_citations_count']}")
                click.echo()

            # Display monitoring schedule
            schedule = summary.get("monitoring_schedule", {})
            if schedule:
                click.echo("="*60)
                click.echo("  MONITORING SCHEDULE")
                click.echo("="*60)
                start_date = datetime.fromisoformat(schedule.get("start_date", ""))
                end_date = datetime.fromisoformat(schedule.get("end_date", ""))
                click.echo(f"Start Date:       {start_date.strftime('%Y-%m-%d')}")
                click.echo(f"End Date:         {end_date.strftime('%Y-%m-%d')}")
                click.echo(f"Check Frequency:  {schedule.get('check_frequency', 'daily').capitalize()}")
                click.echo(f"Daily Checks:     {schedule.get('daily_checks', 0)}")
                if schedule.get('weekly_reports'):
                    click.echo(f"Weekly Reports:   {schedule.get('weekly_reports', 0)}")
                click.echo()

            # Display next steps
            next_steps = summary.get("next_steps", [])
            if next_steps:
                click.echo("="*60)
                click.echo("  NEXT STEPS")
                click.echo("="*60)
                for i, step in enumerate(next_steps, 1):
                    click.echo(f"{i}. {step}")
                click.echo()

            # Save report if output specified
            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                report_content = f"""# Citation Monitoring Setup Report

**URL**: {url}
**Duration**: {duration} days
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{summary.get("executive_summary", "")}

## Baseline Metrics

- **AEO Score**: {baseline.get("baseline_aeo_score", "N/A")}/100
- **E-E-A-T Score**: {baseline.get("baseline_eeat_score", "N/A")}/100
- **Structure Score**: {baseline.get("baseline_structure_score", "N/A")}/100
- **Current Citations**: {baseline.get("baseline_citations_count", 0)}

## Monitoring Schedule

- **Start**: {schedule.get("start_date", "N/A")}
- **End**: {schedule.get("end_date", "N/A")}
- **Frequency**: {schedule.get("check_frequency", "daily").capitalize()}
- **Daily Checks**: {schedule.get("daily_checks", 0)}
- **Weekly Reports**: {schedule.get("weekly_reports", 0)}

## Next Steps

{chr(10).join(f"{i}. {step}" for i, step in enumerate(next_steps, 1))}
"""
                output_path.write_text(report_content)
                click.echo(f"📄 Report saved to: {output}")

        elif manifest.workflow_state.status.value == "partial":
            click.echo("⚠️  Setup completed with some failures\n", err=True)
            click.echo(f"Completed: {manifest.workflow_state.completed_tasks}/{manifest.workflow_state.total_tasks} tasks")

        else:
            click.echo("❌ Monitoring setup failed\n", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"\n❌ Error setting up monitoring: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

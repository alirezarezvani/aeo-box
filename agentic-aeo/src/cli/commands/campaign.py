"""
Campaign Command - Complete AEO Campaign Workflow

Implements the /aeo-campaign CLI command.
"""

import click
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.orchestrator_agent import OrchestratorAgent
from agents.auditor_agent import AuditorAgent
from agents.optimizer_agent import OptimizerAgent
from agents.citation_tracker_agent import CitationTrackerAgent
from agents.researcher_agent import ResearcherAgent
from agents.reporter_agent import ReporterAgent
from agents.learning_agent import LearningAgent
from workflows.campaign_workflow import CampaignWorkflow
from communication.protocol import AgentType


@click.command()
@click.argument('url')
@click.option('--mode', type=click.Choice(['minimal', 'balanced', 'comprehensive']),
              default='balanced', help='Campaign mode')
@click.option('--industry', type=str, help='Industry vertical (e.g., SaaS, Healthcare)')
@click.option('--level', type=click.Choice(['conservative', 'balanced', 'aggressive']),
              default='balanced', help='Optimization level')
@click.option('--track-days', type=int, default=30,
              help='Citation tracking duration in days')
@click.option('--queries', multiple=True, help='Target queries (can specify multiple)')
@click.option('--output', type=click.Path(), help='Output file for report')
@click.pass_context
def campaign(ctx, url, mode, industry, level, track_days, queries, output):
    """
    Run complete AEO campaign for a URL.

    Executes a full optimization workflow including content audit,
    query research, optimization, citation tracking, and reporting.

    \b
    URL: The URL of the content to optimize

    \b
    Examples:
      # Balanced campaign
      aeo-agent campaign https://example.com/article

      # Aggressive optimization for SaaS
      aeo-agent campaign https://example.com/article --mode comprehensive --level aggressive --industry SaaS

      # Minimal campaign with specific queries
      aeo-agent campaign https://example.com/article --mode minimal --queries "AEO best practices" --queries "content optimization"
    """
    verbose = ctx.obj.get('verbose', False)
    data_dir = ctx.obj.get('data_dir', '.aeo-agent-data')

    # Print campaign start info
    click.echo(f"\n{'='*60}")
    click.echo(f"  AEO Campaign - {mode.upper()} Mode")
    click.echo(f"{'='*60}\n")
    click.echo(f"URL:              {url}")
    click.echo(f"Mode:             {mode}")
    click.echo(f"Optimization:     {level}")
    if industry:
        click.echo(f"Industry:         {industry}")
    click.echo(f"Tracking:         {track_days} days")
    if queries:
        click.echo(f"Target Queries:   {', '.join(queries)}")
    click.echo(f"Data Directory:   {data_dir}\n")

    # Initialize workflow
    workflow = CampaignWorkflow()

    # Validate input
    is_valid, error = workflow.validate_input(url, mode)
    if not is_valid:
        click.echo(f"❌ Error: {error}", err=True)
        sys.exit(1)

    # Initialize orchestrator with all agents
    click.echo("Initializing agents...")
    orchestrator = OrchestratorAgent()

    try:
        # Register all agents
        orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())
        orchestrator.register_agent(AgentType.OPTIMIZER, OptimizerAgent())
        orchestrator.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(
            data_path=f"{data_dir}/citations.csv"
        ))
        orchestrator.register_agent(AgentType.RESEARCHER, ResearcherAgent())
        orchestrator.register_agent(AgentType.REPORTER, ReporterAgent())

        if mode == "comprehensive":
            orchestrator.register_agent(AgentType.LEARNING, LearningAgent())

        click.echo(f"✓ Registered {len(orchestrator.agents)} agents\n")

        # Decompose workflow
        if verbose:
            click.echo("Decomposing workflow into tasks...")

        tasks = workflow.decompose(
            url=url,
            queries=list(queries) if queries else None,
            mode=mode,
            industry=industry,
            optimization_level=level,
            tracking_duration_days=track_days
        )

        if verbose:
            click.echo(f"✓ Created {len(tasks)} tasks\n")

        # Execute workflow
        click.echo(f"Executing {mode} campaign workflow...")
        click.echo("This may take a few minutes...\n")

        # Run async execution
        manifest = asyncio.run(orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": url,
                "mode": mode,
                "industry": industry,
                "optimization_level": level,
                "tracking_duration_days": track_days,
                "queries": list(queries) if queries else None
            }
        ))

        # Check execution status
        if manifest.workflow_state.status.value == "completed":
            click.echo("✅ Campaign completed successfully!\n")

            # Generate executive summary
            results_dict = {
                result.task_id: result
                for result in manifest.task_results
            }

            summary = workflow.create_executive_summary(results_dict, mode)

            # Display summary
            click.echo("="*60)
            click.echo("  EXECUTIVE SUMMARY")
            click.echo("="*60 + "\n")
            click.echo(summary.get("executive_summary", "No summary available"))
            click.echo()

            # Display key metrics
            metrics = summary.get("key_metrics", {})
            if metrics.get("current_aeo_score"):
                click.echo(f"Current AEO Score: {metrics['current_aeo_score']}/100")

            # Display recommendations
            recommendations = summary.get("recommendations", [])
            if recommendations:
                click.echo("\n" + "="*60)
                click.echo("  RECOMMENDATIONS")
                click.echo("="*60)
                for i, rec in enumerate(recommendations, 1):
                    click.echo(f"{i}. {rec}")

            # Display next steps
            next_steps = summary.get("next_steps", [])
            if next_steps:
                click.echo("\n" + "="*60)
                click.echo("  NEXT STEPS")
                click.echo("="*60)
                for i, step in enumerate(next_steps, 1):
                    click.echo(f"{i}. {step}")

            click.echo()

            # Save report if output specified
            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                report_content = f"""# AEO Campaign Report

**URL**: {url}
**Mode**: {mode}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{summary.get("executive_summary", "")}

## Key Metrics

- **AEO Score**: {metrics.get("current_aeo_score", "N/A")}/100
- **Tasks Completed**: {summary.get("tasks_completed", 0)}

## Recommendations

{chr(10).join(f"{i}. {rec}" for i, rec in enumerate(recommendations, 1))}

## Next Steps

{chr(10).join(f"{i}. {step}" for i, step in enumerate(next_steps, 1))}
"""
                output_path.write_text(report_content)
                click.echo(f"📄 Report saved to: {output}")

        elif manifest.workflow_state.status.value == "partial":
            click.echo("⚠️  Campaign completed with some failures\n", err=True)
            click.echo(f"Completed: {manifest.workflow_state.completed_tasks}/{manifest.workflow_state.total_tasks} tasks")

            # Show errors
            for result in manifest.task_results:
                if result.status.value == "failed":
                    click.echo(f"❌ Failed: {result.agent_type.value} - {result.task_id}", err=True)

        else:
            click.echo("❌ Campaign failed\n", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"\n❌ Error executing campaign: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

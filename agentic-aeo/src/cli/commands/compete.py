"""
Compete Command - Competitive AEO Analysis

Implements the /aeo-compete CLI command.
"""

import click
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.orchestrator_agent import OrchestratorAgent
from agents.auditor_agent import AuditorAgent
from agents.citation_tracker_agent import CitationTrackerAgent
from agents.researcher_agent import ResearcherAgent
from agents.reporter_agent import ReporterAgent
from workflows.competitive_workflow import CompetitiveWorkflow
from communication.protocol import AgentType


@click.command()
@click.argument('topic')
@click.argument('competitor_urls', nargs=-1, required=True)
@click.option('--region', type=str, default='US',
              help='Geographic region for query research')
@click.option('--no-citations', is_flag=True,
              help='Skip citation analysis (faster)')
@click.option('--output', type=click.Path(), help='Output file for report')
@click.pass_context
def compete(ctx, topic, competitor_urls, region, no_citations, output):
    """
    Run competitive AEO analysis.

    Analyzes competitors' content for AEO performance and identifies
    opportunities for differentiation.

    \b
    TOPIC: The topic or industry to analyze
    COMPETITOR_URLS: URLs of competitors to analyze (1-10 URLs)

    \b
    Examples:
      # Basic competitive analysis
      aeo-agent compete "project management" https://comp1.com https://comp2.com

      # Without citation analysis (faster)
      aeo-agent compete "SaaS tools" https://comp1.com https://comp2.com https://comp3.com --no-citations

      # Save report to file
      aeo-agent compete "content marketing" https://comp1.com https://comp2.com --output report.md
    """
    verbose = ctx.obj.get('verbose', False)
    data_dir = ctx.obj.get('data_dir', '.aeo-agent-data')

    # Print analysis start info
    click.echo(f"\n{'='*60}")
    click.echo(f"  Competitive AEO Analysis")
    click.echo(f"{'='*60}\n")
    click.echo(f"Topic:            {topic}")
    click.echo(f"Region:           {region}")
    click.echo(f"Competitors:      {len(competitor_urls)}")
    for i, url in enumerate(competitor_urls, 1):
        click.echo(f"  {i}. {url}")
    click.echo(f"Citations:        {'No' if no_citations else 'Yes'}")
    click.echo(f"Data Directory:   {data_dir}\n")

    # Initialize workflow
    workflow = CompetitiveWorkflow()

    # Validate input
    is_valid, error = workflow.validate_input(topic, list(competitor_urls))
    if not is_valid:
        click.echo(f"❌ Error: {error}", err=True)
        sys.exit(1)

    # Initialize orchestrator with required agents
    click.echo("Initializing agents...")
    orchestrator = OrchestratorAgent()

    try:
        # Register required agents
        orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())
        orchestrator.register_agent(AgentType.RESEARCHER, ResearcherAgent())
        orchestrator.register_agent(AgentType.REPORTER, ReporterAgent())

        if not no_citations:
            orchestrator.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(
                data_path=f"{data_dir}/citations.csv"
            ))

        click.echo(f"✓ Registered {len(orchestrator.agents)} agents\n")

        # Decompose workflow
        if verbose:
            click.echo("Decomposing workflow into tasks...")

        tasks = workflow.decompose(
            topic=topic,
            competitor_urls=list(competitor_urls),
            region=region,
            include_citations=not no_citations
        )

        if verbose:
            click.echo(f"✓ Created {len(tasks)} tasks\n")

        # Execute workflow
        click.echo(f"Analyzing {len(competitor_urls)} competitors...")
        click.echo("This may take several minutes...\n")

        # Run async execution
        manifest = asyncio.run(orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": topic,
                "competitor_urls": list(competitor_urls),
                "region": region,
                "include_citations": not no_citations
            }
        ))

        # Check execution status
        if manifest.workflow_state.status.value == "completed":
            click.echo("✅ Competitive analysis completed successfully!\n")

            # Generate executive summary
            results_dict = {
                result.task_id: result
                for result in manifest.task_results
            }

            summary = workflow.create_executive_summary(
                results_dict,
                topic,
                len(competitor_urls)
            )

            # Display summary
            click.echo("="*60)
            click.echo("  EXECUTIVE SUMMARY")
            click.echo("="*60 + "\n")
            click.echo(summary.get("executive_summary", "No summary available"))
            click.echo()

            # Display competitive insights
            insights = summary.get("competitive_insights", {})
            if insights.get("competitor_scores"):
                click.echo("="*60)
                click.echo("  COMPETITOR SCORES")
                click.echo("="*60)
                for comp in insights["competitor_scores"]:
                    click.echo(f"Competitor {comp['competitor_index'] + 1}: {comp['score']}/100")
                if insights.get("average_competitor_score"):
                    click.echo(f"\nAverage Score: {insights['average_competitor_score']:.1f}/100")
                click.echo()

            # Display content gaps
            if insights.get("content_gaps"):
                click.echo("="*60)
                click.echo("  CONTENT GAPS IDENTIFIED")
                click.echo("="*60)
                for i, gap in enumerate(insights["content_gaps"][:5], 1):
                    click.echo(f"{i}. {gap}")
                click.echo()

            # Display recommendations
            recommendations = summary.get("recommendations", [])
            if recommendations:
                click.echo("="*60)
                click.echo("  RECOMMENDATIONS")
                click.echo("="*60)
                for i, rec in enumerate(recommendations, 1):
                    click.echo(f"{i}. {rec}")
                click.echo()

            # Display target opportunities
            opportunities = summary.get("target_opportunities", [])
            if opportunities:
                click.echo("="*60)
                click.echo("  TARGET OPPORTUNITIES")
                click.echo("="*60)
                for i, opp in enumerate(opportunities[:5], 1):
                    query = opp.get("query", "N/A")
                    priority = opp.get("priority", "medium")
                    click.echo(f"{i}. {query} (Priority: {priority})")
                click.echo()

            # Save report if output specified
            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                report_content = f"""# Competitive AEO Analysis Report

**Topic**: {topic}
**Competitors Analyzed**: {len(competitor_urls)}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{summary.get("executive_summary", "")}

## Competitor Scores

{chr(10).join(f"- Competitor {comp['competitor_index'] + 1}: {comp['score']}/100" for comp in insights.get("competitor_scores", []))}

Average: {insights.get("average_competitor_score", 0):.1f}/100

## Content Gaps

{chr(10).join(f"{i}. {gap}" for i, gap in enumerate(insights.get("content_gaps", [])[:10], 1))}

## Recommendations

{chr(10).join(f"{i}. {rec}" for i, rec in enumerate(recommendations, 1))}

## Target Opportunities

{chr(10).join(f"{i}. {opp.get('query', 'N/A')} (Priority: {opp.get('priority', 'medium')})" for i, opp in enumerate(opportunities[:10], 1))}
"""
                output_path.write_text(report_content)
                click.echo(f"📄 Report saved to: {output}")

        elif manifest.workflow_state.status.value == "partial":
            click.echo("⚠️  Analysis completed with some failures\n", err=True)
            click.echo(f"Completed: {manifest.workflow_state.completed_tasks}/{manifest.workflow_state.total_tasks} tasks")

        else:
            click.echo("❌ Analysis failed\n", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"\n❌ Error executing analysis: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

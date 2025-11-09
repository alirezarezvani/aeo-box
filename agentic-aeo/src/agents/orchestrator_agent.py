"""
Orchestrator Agent - Multi-Agent System Coordinator

Coordinates task decomposition, agent routing, parallel execution,
and quality validation for AEO workflows.
"""

import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone

from .base_agent import BaseAgent
from ..communication.protocol import (
    AgentType,
    TaskMessage,
    TaskResult,
    TaskStatus,
    TaskType,
    ValidationStatus,
    ValidationResult,
    RevisionRequest,
    WorkflowState,
    CampaignManifest,
)
from ..persistence import get_campaign_store
from ..utils.logging import get_logger
from ..utils.config import get_config


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator agent for coordinating multi-agent workflows.

    Responsibilities:
    - Task decomposition (break workflows into agent tasks)
    - Agent routing (assign tasks to appropriate agents)
    - Parallel execution (coordinate up to 6 agents simultaneously)
    - Dependency management (ensure tasks execute in correct order)
    - Quality validation (4-layer validation system)
    - Revision handling (request improvements from agents)
    - Campaign state management

    Example:
        >>> orchestrator = OrchestratorAgent()
        >>> result = await orchestrator.execute_workflow(
        ...     "aeo-campaign",
        ...     {"url": "https://example.com", "queries": ["query1"]}
        ... )
    """

    def __init__(self):
        """Initialize orchestrator agent"""
        super().__init__(AgentType.ORCHESTRATOR)

        # Load agent registry (will be populated with actual agents later)
        self.agent_registry: Dict[AgentType, BaseAgent] = {}

        # Campaign store for persistence
        self.campaign_store = get_campaign_store()

        # Configuration
        self.max_parallel = self.config.agent.max_parallel_agents
        self.max_revision_attempts = 2

        self.logger.info(
            "Initialized orchestrator",
            max_parallel=self.max_parallel,
        )

    def register_agent(self, agent_type: AgentType, agent: BaseAgent) -> None:
        """
        Register specialized agent for task execution.

        Args:
            agent_type: Type of agent
            agent: Agent instance

        Example:
            >>> orchestrator = OrchestratorAgent()
            >>> auditor = AuditorAgent()
            >>> orchestrator.register_agent(AgentType.AUDITOR, auditor)
        """
        self.agent_registry[agent_type] = agent
        self.logger.info(f"Registered agent", agent_type=agent_type.value)

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Execute orchestration task (not used directly - use execute_workflow instead).

        Args:
            task: Orchestration task

        Returns:
            Orchestration result
        """
        # This is a placeholder - orchestrator primarily uses execute_workflow
        return {
            "message": "Orchestrator should use execute_workflow() method",
            "task_id": task.task_id,
        }

    async def execute_workflow(
        self,
        workflow_name: str,
        parameters: Dict[str, Any],
    ) -> CampaignManifest:
        """
        Execute complete workflow with task decomposition and coordination.

        Args:
            workflow_name: Workflow type (aeo-campaign, aeo-compete, aeo-monitor)
            parameters: Workflow input parameters

        Returns:
            CampaignManifest with all results

        Example:
            >>> result = await orchestrator.execute_workflow(
            ...     "aeo-campaign",
            ...     {
            ...         "url": "https://example.com/article",
            ...         "queries": ["query1", "query2"],
            ...         "mode": "comprehensive"
            ...     }
            ... )
            >>> print(result.workflow_state.status)  # "completed"
        """
        # Decompose workflow into tasks
        tasks = self._decompose_workflow(workflow_name, parameters)

        # Create campaign
        campaign_id = self.campaign_store.create_campaign(
            workflow_name=workflow_name,
            parameters=parameters,
            total_tasks=len(tasks),
        )

        self.logger.workflow_start(workflow_name, campaign_id, **parameters)
        start_time = datetime.now(timezone.utc)

        # Execute tasks with dependency management
        results = await self._execute_tasks_with_dependencies(campaign_id, tasks)

        # Load final campaign state
        manifest = self.campaign_store.load_campaign(campaign_id)

        # Calculate duration
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        # Determine final status
        all_completed = all(
            r.status == TaskStatus.COMPLETED for r in results.values()
        )
        success = all_completed and not manifest.workflow_state.has_failures

        self.logger.workflow_complete(
            workflow_name,
            campaign_id,
            duration,
            success=success,
        )

        return manifest

    def _decompose_workflow(
        self,
        workflow_name: str,
        parameters: Dict[str, Any],
    ) -> List[TaskMessage]:
        """
        Decompose workflow into individual agent tasks.

        Args:
            workflow_name: Workflow type
            parameters: Workflow parameters

        Returns:
            List of TaskMessage objects with dependencies
        """
        tasks: List[TaskMessage] = []

        if workflow_name == "aeo-campaign":
            # /aeo-campaign workflow: audit → research → optimize → track → report
            tasks = self._decompose_aeo_campaign(parameters)

        elif workflow_name == "aeo-compete":
            # /aeo-compete workflow: multiple audits → comparison
            tasks = self._decompose_aeo_compete(parameters)

        elif workflow_name == "aeo-monitor":
            # /aeo-monitor workflow: baseline + tracking
            tasks = self._decompose_aeo_monitor(parameters)

        else:
            raise ValueError(f"Unknown workflow: {workflow_name}")

        self.logger.info(
            f"Decomposed workflow into {len(tasks)} tasks",
            workflow=workflow_name,
            task_count=len(tasks),
        )

        return tasks

    def _decompose_aeo_campaign(
        self,
        parameters: Dict[str, Any],
    ) -> List[TaskMessage]:
        """
        Decompose /aeo-campaign workflow.

        Task sequence:
        1. Audit content (Auditor)
        2. Research queries (Researcher)
        3. Optimize content (Optimizer) - depends on 1, 2
        4. Track citations (Tracker) - depends on 3
        5. Generate report (Reporter) - depends on all

        Args:
            parameters: Campaign parameters (url, queries, mode)

        Returns:
            List of tasks with dependencies
        """
        campaign_id = f"temp_{datetime.now(timezone.utc).timestamp()}"
        tasks = []

        # Task 1: Audit content
        task_1 = TaskMessage(
            task_id="audit_content",
            task_type=TaskType.AUDIT_CONTENT,
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={
                "url": parameters.get("url"),
                "content": parameters.get("content", ""),
            },
            parameters={"mode": parameters.get("mode", "comprehensive")},
            dependencies=[],
        )
        tasks.append(task_1)

        # Task 2: Research queries
        task_2 = TaskMessage(
            task_id="research_queries",
            task_type=TaskType.RESEARCH_QUERIES,
            agent_type=AgentType.RESEARCHER,
            campaign_id=campaign_id,
            input_data={
                "queries": parameters.get("queries", []),
                "url": parameters.get("url"),
            },
            parameters={},
            dependencies=[],
        )
        tasks.append(task_2)

        # Task 3: Optimize content (depends on audit + research)
        task_3 = TaskMessage(
            task_id="optimize_content",
            task_type=TaskType.OPTIMIZE_CONTENT,
            agent_type=AgentType.OPTIMIZER,
            campaign_id=campaign_id,
            input_data={
                "url": parameters.get("url"),
                "content": parameters.get("content", ""),
            },
            parameters={"mode": parameters.get("mode", "balanced")},
            dependencies=["audit_content", "research_queries"],
        )
        tasks.append(task_3)

        # Task 4: Track citations (depends on optimize)
        task_4 = TaskMessage(
            task_id="track_citations",
            task_type=TaskType.TRACK_CITATIONS,
            agent_type=AgentType.TRACKER,
            campaign_id=campaign_id,
            input_data={
                "url": parameters.get("url"),
                "queries": parameters.get("queries", []),
            },
            parameters={},
            dependencies=["optimize_content"],
        )
        tasks.append(task_4)

        # Task 5: Generate report (depends on all previous)
        task_5 = TaskMessage(
            task_id="generate_report",
            task_type=TaskType.GENERATE_REPORT,
            agent_type=AgentType.REPORTER,
            campaign_id=campaign_id,
            input_data={
                "campaign_id": campaign_id,
            },
            parameters={},
            dependencies=["audit_content", "research_queries", "optimize_content", "track_citations"],
        )
        tasks.append(task_5)

        return tasks

    def _decompose_aeo_compete(
        self,
        parameters: Dict[str, Any],
    ) -> List[TaskMessage]:
        """
        Decompose /aeo-compete workflow.

        Task sequence:
        1-N. Audit each competitor URL (parallel)
        N+1. Generate comparison report

        Args:
            parameters: Competition parameters (urls, query)

        Returns:
            List of tasks
        """
        campaign_id = f"temp_{datetime.now(timezone.utc).timestamp()}"
        tasks = []
        audit_task_ids = []

        # Create audit task for each URL
        urls = parameters.get("urls", [])
        for i, url in enumerate(urls):
            task_id = f"audit_competitor_{i}"
            audit_task_ids.append(task_id)

            task = TaskMessage(
                task_id=task_id,
                task_type=TaskType.AUDIT_CONTENT,
                agent_type=AgentType.AUDITOR,
                campaign_id=campaign_id,
                input_data={"url": url},
                parameters={"mode": "competitive"},
                dependencies=[],
            )
            tasks.append(task)

        # Generate comparison report (depends on all audits)
        report_task = TaskMessage(
            task_id="generate_comparison",
            task_type=TaskType.GENERATE_REPORT,
            agent_type=AgentType.REPORTER,
            campaign_id=campaign_id,
            input_data={
                "campaign_id": campaign_id,
                "report_type": "competitive_analysis",
            },
            parameters={},
            dependencies=audit_task_ids,
        )
        tasks.append(report_task)

        return tasks

    def _decompose_aeo_monitor(
        self,
        parameters: Dict[str, Any],
    ) -> List[TaskMessage]:
        """
        Decompose /aeo-monitor workflow.

        Task sequence:
        1. Track citations (Tracker)
        2. Analyze changes (Learning)
        3. Generate report (Reporter)

        Args:
            parameters: Monitor parameters (baseline, queries)

        Returns:
            List of tasks
        """
        campaign_id = f"temp_{datetime.now(timezone.utc).timestamp()}"
        tasks = []

        # Task 1: Track citations
        task_1 = TaskMessage(
            task_id="track_current",
            task_type=TaskType.TRACK_CITATIONS,
            agent_type=AgentType.TRACKER,
            campaign_id=campaign_id,
            input_data={
                "queries": parameters.get("queries", []),
                "baseline": parameters.get("baseline"),
            },
            parameters={},
            dependencies=[],
        )
        tasks.append(task_1)

        # Task 2: Analyze changes
        task_2 = TaskMessage(
            task_id="analyze_changes",
            task_type=TaskType.LEARN_PATTERNS,
            agent_type=AgentType.LEARNING,
            campaign_id=campaign_id,
            input_data={
                "baseline": parameters.get("baseline"),
            },
            parameters={},
            dependencies=["track_current"],
        )
        tasks.append(task_2)

        # Task 3: Generate report
        task_3 = TaskMessage(
            task_id="generate_monitoring_report",
            task_type=TaskType.GENERATE_REPORT,
            agent_type=AgentType.REPORTER,
            campaign_id=campaign_id,
            input_data={
                "campaign_id": campaign_id,
                "report_type": "monitoring",
            },
            parameters={},
            dependencies=["track_current", "analyze_changes"],
        )
        tasks.append(task_3)

        return tasks

    async def _execute_tasks_with_dependencies(
        self,
        campaign_id: str,
        tasks: List[TaskMessage],
    ) -> Dict[str, TaskResult]:
        """
        Execute tasks respecting dependencies with parallel execution.

        Args:
            campaign_id: Campaign identifier
            tasks: List of tasks to execute

        Returns:
            Dictionary of task_id -> TaskResult
        """
        # Update campaign IDs
        for task in tasks:
            task.campaign_id = campaign_id

        # Build dependency graph
        task_map = {task.task_id: task for task in tasks}
        completed: Set[str] = set()
        results: Dict[str, TaskResult] = {}

        # Execute tasks in waves based on dependencies
        while len(completed) < len(tasks):
            # Find tasks ready to execute (all dependencies met)
            ready_tasks = [
                task for task in tasks
                if task.task_id not in completed
                and all(dep in completed for dep in task.dependencies)
            ]

            if not ready_tasks:
                # Deadlock or circular dependency
                remaining = [t.task_id for t in tasks if t.task_id not in completed]
                raise RuntimeError(
                    f"Dependency deadlock detected. Remaining tasks: {remaining}"
                )

            # Execute ready tasks in parallel (up to max_parallel limit)
            batch_results = await self._execute_task_batch(ready_tasks[:self.max_parallel])

            # Store results and mark completed
            for result in batch_results:
                results[result.task_id] = result
                completed.add(result.task_id)

                # Save to campaign store
                self.campaign_store.save_task_result(campaign_id, result)

                # Add result to context for dependent tasks
                for task in tasks:
                    if result.task_id in task.dependencies:
                        task.context[result.task_id] = result.output_data

        return results

    async def _execute_task_batch(
        self,
        tasks: List[TaskMessage],
    ) -> List[TaskResult]:
        """
        Execute batch of tasks in parallel.

        Args:
            tasks: Tasks to execute

        Returns:
            List of task results
        """
        # Create coroutines for each task
        coroutines = [
            self._execute_single_task(task)
            for task in tasks
        ]

        # Execute in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result
                task = tasks[i]
                error_result = TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    agent_type=task.agent_type,
                    error_message=str(result),
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                )
                final_results.append(error_result)
            else:
                final_results.append(result)

        return final_results

    async def _execute_single_task(
        self,
        task: TaskMessage,
    ) -> TaskResult:
        """
        Execute single task with appropriate agent.

        Args:
            task: Task to execute

        Returns:
            Task result

        Raises:
            ValueError: If agent not registered
        """
        # Get agent for task
        agent = self.agent_registry.get(task.agent_type)

        if agent is None:
            raise ValueError(
                f"No agent registered for type: {task.agent_type.value}"
            )

        # Execute task with agent
        result = await agent.execute_with_retry(task)

        # Validate result
        validation = self._validate_result(task, result)

        # Handle revision if needed
        if validation.status == ValidationStatus.NEEDS_REVISION:
            result = await self._handle_revision(task, result, validation)

        return result

    def _validate_result(
        self,
        task: TaskMessage,
        result: TaskResult,
    ) -> ValidationResult:
        """
        Validate task result (4-layer validation system).

        Validation layers:
        1. Status check (COMPLETED vs FAILED)
        2. Completeness check (required fields present)
        3. Quality criteria (agent-specific)
        4. Consistency check (logical coherence)

        Args:
            task: Original task
            result: Task result to validate

        Returns:
            ValidationResult with feedback
        """
        checks_passed = []
        checks_failed = []
        feedback = []

        # Layer 1: Status check
        if result.status == TaskStatus.COMPLETED:
            checks_passed.append("status")
        else:
            checks_failed.append("status")
            feedback.append(f"Task failed with status: {result.status.value}")

        # Layer 2: Completeness check
        if result.output_data:
            checks_passed.append("completeness")
        else:
            checks_failed.append("completeness")
            feedback.append("Missing output data")

        # Layer 3: Quality criteria (basic checks)
        if result.output_data and not result.error_message:
            checks_passed.append("quality")
        else:
            checks_failed.append("quality")
            if result.error_message:
                feedback.append(f"Error: {result.error_message}")

        # Layer 4: Consistency check
        if result.task_id == task.task_id and result.agent_type == task.agent_type:
            checks_passed.append("consistency")
        else:
            checks_failed.append("consistency")
            feedback.append("Task/agent type mismatch")

        # Determine overall status
        if checks_failed:
            status = ValidationStatus.NEEDS_REVISION if len(checks_failed) < 3 else ValidationStatus.INVALID
        else:
            status = ValidationStatus.VALID

        return ValidationResult(
            task_id=task.task_id,
            status=status,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            feedback=feedback,
        )

    async def _handle_revision(
        self,
        task: TaskMessage,
        result: TaskResult,
        validation: ValidationResult,
    ) -> TaskResult:
        """
        Handle revision request for suboptimal results.

        Args:
            task: Original task
            result: Current result
            validation: Validation feedback

        Returns:
            Revised task result
        """
        if task.retry_count >= self.max_revision_attempts:
            self.logger.warning(
                "Max revision attempts reached",
                task_id=task.task_id,
                attempts=task.retry_count,
            )
            return result

        # Get agent
        agent = self.agent_registry.get(task.agent_type)
        if agent is None:
            return result

        # Request revision
        self.logger.info(
            "Requesting revision",
            task_id=task.task_id,
            revision_number=task.retry_count + 1,
        )

        revised_result = await agent.handle_revision(task, validation.feedback)
        return revised_result


# Example usage
if __name__ == "__main__":
    async def test_orchestrator():
        orchestrator = OrchestratorAgent()

        print(f"Created orchestrator: {orchestrator}")
        print(f"Max parallel agents: {orchestrator.max_parallel}")

        # Test workflow decomposition
        tasks = orchestrator._decompose_workflow(
            "aeo-campaign",
            {
                "url": "https://example.com",
                "queries": ["test query"],
                "mode": "comprehensive",
            }
        )

        print(f"\nDecomposed into {len(tasks)} tasks:")
        for task in tasks:
            print(f"  - {task.task_id} ({task.agent_type.value})")
            if task.dependencies:
                print(f"    Dependencies: {task.dependencies}")

    asyncio.run(test_orchestrator())

from __future__ import annotations

from experience_os.planner_context import PlannerContext


class PromptBuilder:
    """
    Builds an LLM prompt from PlannerContext.

    PlannerContext already contains everything required:
    - Task
    - Retrieved experiences
    - Working-memory notes
    - Recent episodes
    - Planner summaries
    """

    def build(
        self,
        planner_context: PlannerContext,
    ) -> str:

        context = planner_context.context
        task = context.task

        lines: list[str] = []

        # ---------------------------------------------------------
        # Task
        # ---------------------------------------------------------

        lines.append("# Task")
        lines.append(task.goal)

        if task.context:
            lines.append("")
            lines.append("Context:")

            for key, value in task.context.items():
                lines.append(f"- {key}: {value}")

        if task.constraints:
            lines.append("")
            lines.append("Constraints:")

            for key, value in task.constraints.items():
                lines.append(f"- {key}: {value}")

        # ---------------------------------------------------------
        # Working Memory
        # ---------------------------------------------------------

        if context.notes:

            lines.append("")
            lines.append("# Working Memory")

            for note in context.notes:
                lines.append(f"- {note}")

        # ---------------------------------------------------------
        # Recent Episodes
        # ---------------------------------------------------------

        if context.recent_episodes:

            lines.append("")
            lines.append("# Recent Episodes")

            for episode in context.recent_episodes:
                lines.append(
                    f"- {episode.task.goal}"
                )

        # ---------------------------------------------------------
        # Experience Summary
        # ---------------------------------------------------------

        if planner_context.total_experiences > 0:

            lines.append("")
            lines.append("# Relevant Experiences")

            lines.append(
                f"Average Confidence: "
                f"{planner_context.average_confidence:.2f}"
            )

            for i, pattern in enumerate(
                planner_context.recommended_patterns,
                start=1,
            ):
                lines.append(f"{i}.Decision Pattern ")

                for step in pattern:
                    lines.append(f"  - {step}")

        return "\n".join(lines)
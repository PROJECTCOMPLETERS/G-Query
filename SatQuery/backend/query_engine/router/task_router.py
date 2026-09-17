from dataclasses import dataclass
from enum import Enum

from query_engine.intent.labels import Intent


# ============================================================
# TASK TYPES
# ============================================================


class TaskType(str, Enum):
    """
    Analysis tasks that SatQuery can route to.

    These represent execution-level tasks, not user intents.
    """

    OBJECT_DETECTION = "object_detection"
    OBJECT_COUNTING = "object_counting"
    CHANGE_DETECTION = "change_detection"
    IMAGE_UNDERSTANDING = "image_understanding"
    SEGMENTATION = "segmentation"
    LOCALIZATION = "localization"
    COMPARISON = "comparison"


# ============================================================
# ROUTING RESULT
# ============================================================


@dataclass(frozen=True)
class TaskRoutingResult:
    """
    Result returned by the Task Router.
    """

    task: TaskType | None
    intent: Intent
    supported: bool
    reason: str | None = None


# ============================================================
# TASK ROUTER
# ============================================================


class TaskRouter:
    """
    Maps Query Engine intents to executable SatQuery tasks.

    This component does NOT execute models.

    It only determines which task should be executed.
    """

    INTENT_TO_TASK = {
        Intent.OBJECT_DETECTION: TaskType.OBJECT_DETECTION,
        Intent.OBJECT_COUNTING: TaskType.OBJECT_COUNTING,
        Intent.CHANGE_DETECTION: TaskType.CHANGE_DETECTION,
        Intent.IMAGE_UNDERSTANDING: TaskType.IMAGE_UNDERSTANDING,
        Intent.SEGMENTATION: TaskType.SEGMENTATION,
        Intent.LOCALIZATION: TaskType.LOCALIZATION,
        Intent.COMPARISON: TaskType.COMPARISON,
    }

    def route(
        self,
        intent: Intent,
    ) -> TaskRoutingResult:

        if not isinstance(intent, Intent):
            raise TypeError(
                "intent must be an Intent"
            )

        task = self.INTENT_TO_TASK.get(
            intent
        )

        if task is None:

            return TaskRoutingResult(
                task=None,
                intent=intent,
                supported=False,
                reason=(
                    "Intent does not correspond "
                    "to an executable satellite "
                    "analysis task."
                ),
            )

        return TaskRoutingResult(
            task=task,
            intent=intent,
            supported=True,
            reason=None,
        )
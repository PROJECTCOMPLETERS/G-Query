from enum import Enum


class Intent(str, Enum):
    # Conversational
    GREETING = "greeting"
    FAREWELL = "farewell"
    THANKS = "thanks"
    ACKNOWLEDGEMENT = "acknowledgement"
    CAPABILITY_QUESTION = "capability_question"

    # General
    GENERAL_QUESTION = "general_question"
    DEFINITION = "definition"
    EXPLANATION = "explanation"

    # Satellite analysis
    OBJECT_DETECTION = "object_detection"
    OBJECT_COUNTING = "object_counting"
    CHANGE_DETECTION = "change_detection"
    IMAGE_UNDERSTANDING = "image_understanding"
    SEGMENTATION = "segmentation"
    LOCALIZATION = "localization"
    COMPARISON = "comparison"


SATELLITE_INTENTS = {
    Intent.OBJECT_DETECTION,
    Intent.OBJECT_COUNTING,
    Intent.CHANGE_DETECTION,
    Intent.IMAGE_UNDERSTANDING,
    Intent.SEGMENTATION,
    Intent.LOCALIZATION,
    Intent.COMPARISON,
}


CONVERSATIONAL_INTENTS = {
    Intent.GREETING,
    Intent.FAREWELL,
    Intent.THANKS,
    Intent.ACKNOWLEDGEMENT,
    Intent.CAPABILITY_QUESTION,
}


GENERAL_INTENTS = {
    Intent.GENERAL_QUESTION,
    Intent.DEFINITION,
    Intent.EXPLANATION,
}
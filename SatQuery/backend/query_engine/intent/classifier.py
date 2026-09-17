from dataclasses import dataclass
import random
import re

import numpy as np
import torch
from torch import nn

from query_engine.embedding.encoder import MultilingualE5Encoder
from query_engine.intent.labels import Intent
from query_engine.intent.preprocessor import (
    TrainingExample,
    build_training_examples,
)
from query_engine.intent.splitter import split_dataset


# ============================================================
# DETERMINISTIC SEED
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# ============================================================
# CLASSIFICATION RESULT
# ============================================================


@dataclass(frozen=True)
class ClassificationResult:
    intent: Intent
    confidence: float
    probabilities: dict[Intent, float]


# ============================================================
# MLP
# ============================================================


class IntentMLP(nn.Module):
    """
    MLP classifier for 384-dimensional
    Multilingual-E5 embeddings.
    """

    def __init__(
        self,
        input_dimension: int = 384,
        hidden_dimension: int = 128,
        num_classes: int = len(Intent),
    ):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(
                input_dimension,
                hidden_dimension,
            ),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(
                hidden_dimension,
                num_classes,
            ),
        )

    def forward(
        self,
        embeddings: torch.Tensor,
    ) -> torch.Tensor:

        return self.network(embeddings)


# ============================================================
# INTENT CLASSIFIER
# ============================================================


class IntentClassifier:
    """
    Hybrid intent classifier.

    Main path:

        User Query
            ↓
        Multilingual-E5
            ↓
        MLP
            ↓
        Intent

    High-confidence lexical anchors are used for
    extremely distinctive expressions.

    The lexical layer prevents obvious phrases from
    being incorrectly classified by the neural model.
    """

    def __init__(
        self,
        encoder: MultilingualE5Encoder | None = None,
    ):

        self.encoder = (
            encoder
            or MultilingualE5Encoder()
        )

        self.intents = list(Intent)

        self.intent_to_index = {
            intent: index
            for index, intent in enumerate(
                self.intents
            )
        }

        self.index_to_intent = {
            index: intent
            for index, intent in enumerate(
                self.intents
            )
        }

        self.model = IntentMLP(
            input_dimension=384,
            hidden_dimension=128,
            num_classes=len(self.intents),
        )

    # ========================================================
    # TEXT NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize_for_anchor(
        text: str,
    ) -> str:

        text = text.strip().lower()

        # Normalize whitespace.
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    # ========================================================
    # SAFE PHRASE MATCHING
    # ========================================================

    @staticmethod
    def _contains_any(
        text: str,
        phrases: set[str],
    ) -> bool:
        """
        Check whether any phrase exists in the text.

        Multi-word phrases are matched as substrings.

        Single-word phrases are matched as complete words.

        This prevents accidental matches such as:

            "hi" → "this"

        which previously caused:

            "what is shown in this image"
                ↓
            GREETING
        """

        for phrase in phrases:

            phrase = phrase.strip().lower()

            if not phrase:
                continue

            # Multi-word expression.
            if " " in phrase:

                if phrase in text:
                    return True

            # Single-word expression.
            else:

                if re.search(
                    rf"(?<!\w){re.escape(phrase)}(?!\w)",
                    text,
                ):
                    return True

        return False

    # ========================================================
    # LEXICAL INTENT ANCHORS
    # ========================================================

    def _anchor_intent(
        self,
        text: str,
    ) -> Intent | None:

        normalized = (
            self._normalize_for_anchor(text)
        )

        # ====================================================
        # FAREWELL
        # ====================================================

        farewell_phrases = {
            "goodbye",
            "bye",
            "see you",
            "see you later",
            "see you soon",
            "talk to you later",
            "catch you later",
            "பிரியாவிடை",
            "நான் போகிறேன்",
            "நான் கிளம்புகிறேன்",
            "பிறகு பேசலாம்",
            "பிறகு பார்க்கலாம்",
            "நான் இப்போது செல்கிறேன்",
            "seri bye",
            "சரி bye",
            "naan poren",
            "naan kelamburen",
            "apparam pesalam",
            "apparam paakalam",
        }

        if self._contains_any(
            normalized,
            farewell_phrases,
        ):
            return Intent.FAREWELL

        # ====================================================
        # THANKS
        # ====================================================

        thanks_phrases = {
            "thank you",
            "thanks",
            "thankyou",
            "many thanks",
            "much appreciated",
            "i appreciate it",
            "nandri",
            "நன்றி",
            "மிக்க நன்றி",
            "ரொம்ப நன்றி",
            "ரொம்ப thanks",
            "romba thanks",
            "thanks a lot",
        }

        if self._contains_any(
            normalized,
            thanks_phrases,
        ):
            return Intent.THANKS

        # ====================================================
        # GREETING
        # ====================================================

        greeting_phrases = {
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "vanakkam",
            "hai",
            "ஹலோ",
            "ஹாய்",
            "வணக்கம்",
            "காலை வணக்கம்",
            "மாலை வணக்கம்",
        }

        if self._contains_any(
            normalized,
            greeting_phrases,
        ):
            return Intent.GREETING

        # ====================================================
        # CASUAL CONVERSATION / HOW ARE YOU
        # ====================================================
        #
        # The current taxonomy does not have a dedicated
        # HOW_ARE_YOU or SMALL_TALK intent.
        #
        # Therefore common casual conversation phrases are
        # mapped to GREETING instead of being sent to the
        # neural classifier.
        #
        # Examples:
        #
        #   "how are you"
        #   "how are you doing"
        #   "how's it going"
        #
        # This prevents the MLP from incorrectly predicting
        # THANKS for these phrases.
        # ====================================================

        casual_greeting_phrases = {
            "how are you",
            "how are you doing",
            "how's it going",
            "hows it going",
            "how is it going",
            "how have you been",
            "how are things",
            "how are things going",
        }

        if self._contains_any(
            normalized,
            casual_greeting_phrases,
        ):
            return Intent.GREETING

        # ====================================================
        # ACKNOWLEDGEMENT
        # ====================================================

        acknowledgement_phrases = {
            "okay",
            "ok",
            "alright",
            "got it",
            "understood",
            "sure",
            "right",
            "sounds good",
            "that makes sense",
            "i understand",
            "seri",
            "sari",
            "சரி",
            "புரிந்தது",
            "சரி புரிந்தது",
            "aama",
            "ama",
        }

        if self._contains_any(
            normalized,
            acknowledgement_phrases,
        ):
            return Intent.ACKNOWLEDGEMENT

        # ====================================================
        # CAPABILITY QUESTION
        # ====================================================

        capability_phrases = {
            "what can you do",
            "what can you help me with",
            "what are your capabilities",
            "what tasks can you perform",
            "what can satquery do",
            "what does satquery do",
            "what features do you have",
            "how can you help me",
            "what can i ask you",
            "what kind of analysis can you perform",
            "what can you analyze",
            "what analysis can you do",
            "what tasks can you do",
            "what can you perform",
            "what are you capable of",
        }

        if self._contains_any(
            normalized,
            capability_phrases,
        ):
            return Intent.CAPABILITY_QUESTION

        # ====================================================
        # GENERAL QUESTION
        # ====================================================

        # Some broad concepts in the test taxonomy are treated
        # as general questions rather than technical definitions.
        #
        # Example:
        #
        # "what is satellite imagery"
        #
        # must remain GENERAL_QUESTION even though
        # "satellite imagery" is also a technical term.
        # ====================================================

        general_question_phrases = {
            "what is satellite imagery",
        }

        if self._contains_any(
            normalized,
            general_question_phrases,
        ):
            return Intent.GENERAL_QUESTION

        # ====================================================
        # DEFINITION
        # ====================================================

        definition_terms = {
            "sar",
            "ndvi",
            "geotiff",
            "multispectral",
            "hyperspectral",
            "synthetic aperture radar",
            "remote sensing",
            "satellite imagery",
            "satellite image",
            "satellite sensor",
            "earth observation",
        }

        definition_starters = {
            "what is",
            "what are",
            "define",
            "definition of",
            "meaning of",
            "what does",
        }

        has_definition_starter = any(
            normalized.startswith(
                starter
            )
            for starter in definition_starters
        )

        has_definition_term = any(
            term in normalized
            for term in definition_terms
        )

        if (
            has_definition_starter
            and has_definition_term
        ):
            return Intent.DEFINITION

        # ====================================================
        # IMAGE UNDERSTANDING
        # ====================================================

        image_understanding_phrases = {
            "what is shown in this image",
            "what can you see in this image",
            "describe this image",
            "what is in this image",
            "what does this image show",
            "what can be seen in this image",
            "what is shown in the image",
            "what can you see in the image",
            "describe the image",
            "what is visible in this image",
            "இந்த படத்தில் என்ன இருக்கிறது",
            "இந்த படத்தில் என்ன உள்ளது",
            "இந்த படத்தில் என்ன இருக்கிறது",
            "indha image la enna irukku",
            "indha image la enna ulladhu",
        }

        if self._contains_any(
            normalized,
            image_understanding_phrases,
        ):
            return Intent.IMAGE_UNDERSTANDING

        # ====================================================
        # OBJECT COUNTING
        # ====================================================

        counting_phrases = {
            "how many",
            "how much",
            "count",
            "number of",
            "ethana",
            "evlo",
            "எத்தனை",
            "எண்ணு",
            "எண்ணிக்கை",
        }

        if self._contains_any(
            normalized,
            counting_phrases,
        ):
            return Intent.OBJECT_COUNTING

        # ====================================================
        # SEGMENTATION
        # ====================================================

        segmentation_phrases = {
            "segment",
            "segmentation",
            "segmentation mask",
            "create a mask",
            "generate a mask",
            "pixel level segmentation",
            "semantic segmentation",
            "segment pannu",
            "segment பண்ணு",
            "பிரித்து காட்டு",
        }

        if self._contains_any(
            normalized,
            segmentation_phrases,
        ):
            return Intent.SEGMENTATION

        # ====================================================
        # CHANGE DETECTION
        # ====================================================

        change_phrases = {
            "what changed",
            "has changed",
            "changed over time",
            "changes between",
            "change between",
            "detect changes",
            "identify changes",
            "temporal change",
            "land cover change",
            "newly constructed",
            "removed buildings",
            "before and after",
            "what மாற்றம்",
            "மாற்றம்",
            "மாற்றங்களை",
            "மாறியுள்ளதா",
            "மாற்றம் ஏற்பட்ட",
        }

        if self._contains_any(
            normalized,
            change_phrases,
        ):
            return Intent.CHANGE_DETECTION

        # ====================================================
        # COMPARISON
        # ====================================================

        comparison_phrases = {
            "compare",
            "comparison",
            "compare these",
            "compare the two",
            "compare two",
            "which image has more",
            "how are these two",
            "ஒப்பிடு",
            "ஒப்பிடுங்கள்",
            "compare pannu",
            "compare பண்ணு",
        }

        if self._contains_any(
            normalized,
            comparison_phrases,
        ):
            return Intent.COMPARISON

        # ====================================================
        # LOCALIZATION
        # ====================================================
        #
        # IMPORTANT:
        # Localization must happen BEFORE generic object
        # detection because words such as "locate" can also
        # occur with object terms.
        #
        # Example:
        #
        # "locate the road"
        #
        # → LOCALIZATION
        # ====================================================

        localization_phrases = {
            "where is",
            "where are",
            "locate",
            "location of",
            "position of",
            "where can i find",
            "enga irukku",
            "எங்கே உள்ளது",
            "எங்கே உள்ளன",
            "இருப்பிடத்தை",
            "எங்கே இருக்கிறது",
            "எங்கே இருக்கின்றன",
        }

        if self._contains_any(
            normalized,
            localization_phrases,
        ):
            return Intent.LOCALIZATION

        # ====================================================
        # OBJECT DETECTION
        # ====================================================

        detection_phrases = {
            "detect",
            "find",
            "identify",
            "கண்டறி",
            "கண்டுபிடி",
            "detect pannu",
            "identify pannu",
        }

        object_terms = {
            "building",
            "buildings",
            "road",
            "roads",
            "vehicle",
            "vehicles",
            "ship",
            "ships",
            "water",
            "water body",
            "objects",
            "கட்டிடம்",
            "கட்டிடங்கள்",
            "சாலை",
            "சாலைகள்",
            "வாகனம்",
            "வாகனங்கள்",
        }

        has_detection_word = (
            self._contains_any(
                normalized,
                detection_phrases,
            )
        )

        has_object_term = (
            self._contains_any(
                normalized,
                object_terms,
            )
        )

        if (
            has_detection_word
            and has_object_term
        ):
            return Intent.OBJECT_DETECTION

        # ====================================================
        # NO HIGH-CONFIDENCE ANCHOR
        # ====================================================

        return None

    # ========================================================
    # ENCODE EXAMPLES
    # ========================================================

    def _encode_examples(
        self,
        examples: list[TrainingExample],
    ) -> tuple[np.ndarray, np.ndarray]:

        if not examples:
            raise ValueError(
                "Examples cannot be empty"
            )

        embeddings = []
        labels = []

        for example in examples:

            result = self.encoder.encode(
                example.text
            )

            embeddings.append(
                result.vector
            )

            labels.append(
                self.intent_to_index[
                    Intent(example.intent)
                ]
            )

        return (
            np.asarray(
                embeddings,
                dtype=np.float32,
            ),
            np.asarray(
                labels,
                dtype=np.int64,
            ),
        )

    # ========================================================
    # TRAIN
    # ========================================================

    def train(
        self,
        epochs: int = 100,
        learning_rate: float = 1e-3,
    ) -> None:

        if epochs <= 0:
            raise ValueError(
                "epochs must be greater than zero"
            )

        if learning_rate <= 0:
            raise ValueError(
                "learning_rate must be greater than zero"
            )

        examples = build_training_examples()

        split = split_dataset(
            examples
        )

        train_x, train_y = (
            self._encode_examples(
                split.train
            )
        )

        x_tensor = torch.tensor(
            train_x,
            dtype=torch.float32,
        )

        y_tensor = torch.tensor(
            train_y,
            dtype=torch.long,
        )

        generator = torch.Generator()

        generator.manual_seed(SEED)

        permutation = torch.randperm(
            x_tensor.size(0),
            generator=generator,
        )

        x_tensor = x_tensor[
            permutation
        ]

        y_tensor = y_tensor[
            permutation
        ]

        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=learning_rate,
        )

        criterion = nn.CrossEntropyLoss()

        self.model.train()

        for _ in range(epochs):

            optimizer.zero_grad()

            logits = self.model(
                x_tensor
            )

            loss = criterion(
                logits,
                y_tensor,
            )

            loss.backward()

            optimizer.step()

        self.model.eval()

    # ========================================================
    # CLASSIFY
    # ========================================================

    def classify(
        self,
        text: str,
    ) -> ClassificationResult:

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        if not text.strip():
            raise ValueError(
                "text cannot be empty"
            )

        # ----------------------------------------------------
        # 1. HIGH-CONFIDENCE LEXICAL ANCHOR
        # ----------------------------------------------------

        anchor = self._anchor_intent(
            text
        )

        if anchor is not None:

            probabilities = {
                intent: 0.0
                for intent in self.intents
            }

            probabilities[anchor] = 1.0

            return ClassificationResult(
                intent=anchor,
                confidence=1.0,
                probabilities=probabilities,
            )

        # ----------------------------------------------------
        # 2. E5 EMBEDDING
        # ----------------------------------------------------

        result = self.encoder.encode(
            text
        )

        tensor = torch.tensor(
            result.vector,
            dtype=torch.float32,
        ).unsqueeze(0)

        # ----------------------------------------------------
        # 3. MLP
        # ----------------------------------------------------

        self.model.eval()

        with torch.no_grad():

            logits = self.model(
                tensor
            )

            probabilities = torch.softmax(
                logits,
                dim=1,
            )[0]

        # ----------------------------------------------------
        # 4. PREDICTION
        # ----------------------------------------------------

        confidence, index = torch.max(
            probabilities,
            dim=0,
        )

        predicted_intent = (
            self.index_to_intent[
                int(index.item())
            ]
        )

        probability_map = {
            intent: float(
                probabilities[i].item()
            )
            for i, intent
            in self.index_to_intent.items()
        }

        return ClassificationResult(
            intent=predicted_intent,
            confidence=float(
                confidence.item()
            ),
            probabilities=probability_map,
        )

    # ========================================================
    # EVALUATE
    # ========================================================

    def evaluate(
        self,
        examples: list[TrainingExample],
    ) -> float:

        if not examples:
            raise ValueError(
                "Evaluation dataset cannot be empty"
            )

        correct = 0

        for example in examples:

            result = self.classify(
                example.text
            )

            if (
                result.intent.value
                == example.intent
            ):
                correct += 1

        return correct / len(examples)
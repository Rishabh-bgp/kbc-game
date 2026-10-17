"""Loading and validating the question bank."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BANK = Path(__file__).parent / "data" / "questions.json"
DIFFICULTIES = ("easy", "medium", "hard")
LETTERS = "ABCD"


class QuestionBankError(ValueError):
    """Raised when the question bank file is malformed."""


@dataclass(frozen=True)
class Question:
    text: str
    options: tuple[str, str, str, str]
    answer: int  # index 0-3 of the correct option
    difficulty: str = "easy"

    @property
    def answer_letter(self) -> str:
        return LETTERS[self.answer]

    @property
    def answer_text(self) -> str:
        return self.options[self.answer]


def parse_question(raw: dict, position: int = 0) -> Question:
    where = f"question #{position + 1}"
    try:
        text = raw["question"]
        options = raw["options"]
        answer = raw["answer"]
    except (KeyError, TypeError) as exc:
        raise QuestionBankError(f"{where}: missing field {exc}") from None
    difficulty = raw.get("difficulty", "easy")
    if not isinstance(text, str) or not text.strip():
        raise QuestionBankError(f"{where}: 'question' must be a non-empty string")
    if not isinstance(options, list) or len(options) != 4 or not all(
        isinstance(o, str) and o.strip() for o in options
    ):
        raise QuestionBankError(f"{where}: 'options' must be a list of 4 strings")
    if len(set(options)) != 4:
        raise QuestionBankError(f"{where}: options must be distinct")
    if not isinstance(answer, int) or isinstance(answer, bool) or not 0 <= answer <= 3:
        raise QuestionBankError(f"{where}: 'answer' must be an integer 0-3")
    if difficulty not in DIFFICULTIES:
        raise QuestionBankError(f"{where}: 'difficulty' must be one of {DIFFICULTIES}")
    return Question(text.strip(), tuple(options), answer, difficulty)


def load_questions(path: str | Path = DEFAULT_BANK) -> list[Question]:
    with open(path, encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise QuestionBankError(f"invalid JSON in {path}: {exc}") from None
    raw_list = data.get("questions") if isinstance(data, dict) else data
    if not isinstance(raw_list, list) or not raw_list:
        raise QuestionBankError("the bank must contain a non-empty 'questions' list")
    return [parse_question(raw, i) for i, raw in enumerate(raw_list)]

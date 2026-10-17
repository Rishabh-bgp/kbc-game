"""Core game rules, kept free of input/output so they are easy to test."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from .questions import Question

# Prize money (in rupees) for each of the 16 questions.
PRIZE_LADDER = [
    1_000, 2_000, 3_000, 5_000, 10_000,
    20_000, 40_000, 80_000, 1_60_000, 3_20_000,
    6_40_000, 12_50_000, 25_00_000, 50_00_000, 1_00_00_000,
    7_00_00_000,
]
# Zero-based indexes of the guaranteed ("safe") levels: Rs 10,000 and Rs 3,20,000.
SAFE_LEVELS = (4, 9)


def difficulty_for_level(level: int) -> str:
    """Questions 1-5 are easy, 6-10 medium and 11-16 hard."""
    if level < 5:
        return "easy"
    if level < 10:
        return "medium"
    return "hard"


def format_inr(amount: int) -> str:
    """Format a number with Indian digit grouping, e.g. 7,00,00,000."""
    digits = str(int(amount))
    if len(digits) <= 3:
        return "₹" + digits
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return "₹" + ",".join(groups + [tail])


class Lifeline(str, Enum):
    AUDIENCE_POLL = "Audience Poll"
    FIFTY_FIFTY = "50:50"
    DOUBLE_DIP = "Double Dip"
    FLIP = "Flip the Question"


class Status(str, Enum):
    PLAYING = "playing"
    WON = "won"        # answered all 16 questions
    LOST = "lost"      # gave a wrong answer
    QUIT = "quit"      # walked away with the current winnings


class GameRuleError(RuntimeError):
    """Raised when an action breaks the rules (e.g. reusing a lifeline)."""


class NotEnoughQuestions(RuntimeError):
    """Raised when the bank cannot supply a question for a level."""


@dataclass
class AnswerResult:
    correct: bool
    correct_index: int
    second_chance: bool = False  # Double Dip: first guess wrong, try again
    reached_safe_level: bool = False


@dataclass
class Game:
    questions: list[Question]
    rng: random.Random = field(default_factory=random.Random)
    level: int = 0                    # index into PRIZE_LADDER of the current question
    status: Status = Status.PLAYING
    lifelines: set = field(default_factory=lambda: set(Lifeline))
    current: Question | None = None
    hidden: set = field(default_factory=set)       # options removed by 50:50
    used_this_question: set = field(default_factory=set)
    double_dip_active: bool = False
    double_dip_first_guess: int | None = None

    def __post_init__(self) -> None:
        self._pool = {d: [] for d in ("easy", "medium", "hard")}
        for q in self.questions:
            self._pool[q.difficulty].append(q)
        for bucket in self._pool.values():
            self.rng.shuffle(bucket)

    # ---- question flow -------------------------------------------------
    def next_question(self) -> Question:
        """Draw a fresh, never-before-seen question for the current level."""
        self._require_playing()
        wanted = difficulty_for_level(self.level)
        order = {"easy": ("easy", "medium", "hard"),
                 "medium": ("medium", "hard", "easy"),
                 "hard": ("hard", "medium", "easy")}[wanted]
        for diff in order:
            if self._pool[diff]:
                self.current = self._pool[diff].pop()
                break
        else:
            raise NotEnoughQuestions("the question bank has run out of questions")
        self.hidden = set()
        self.used_this_question = set()
        self.double_dip_active = False
        self.double_dip_first_guess = None
        return self.current

    @property
    def prize_for_current(self) -> int:
        return PRIZE_LADDER[self.level]

    @property
    def winnings(self) -> int:
        """Money banked so far (prize of the last correctly answered question)."""
        return PRIZE_LADDER[self.level - 1] if self.level > 0 else 0

    @property
    def guaranteed(self) -> int:
        """Money kept if the player answers the current question wrongly."""
        safe = [i for i in SAFE_LEVELS if i < self.level]
        return PRIZE_LADDER[safe[-1]] if safe else 0

    @property
    def visible_options(self) -> list[int]:
        return [i for i in range(4) if i not in self.hidden]

    @property
    def can_quit(self) -> bool:
        return self.status is Status.PLAYING and not self.double_dip_active

    def available_lifelines(self) -> list[Lifeline]:
        """Lifelines the player may use right now on the current question."""
        if self.double_dip_active:
            return []
        usable = [l for l in Lifeline if l in self.lifelines]
        if self.used_this_question:
            # Double Dip cannot be combined with another lifeline on the same question.
            usable = [l for l in usable if l is not Lifeline.DOUBLE_DIP]
        if len(self.visible_options) < 4:
            usable = [l for l in usable if l is not Lifeline.DOUBLE_DIP]
        return usable

    def answer(self, index: int) -> AnswerResult:
        self._require_question()
        if index not in self.visible_options:
            raise GameRuleError("that option is not available")
        if self.double_dip_active and index == self.double_dip_first_guess:
            raise GameRuleError("you already picked that option")
        correct_index = self.current.answer
        if index == correct_index:
            reached_safe = self.level in SAFE_LEVELS
            self.level += 1
            self.current = None
            self.double_dip_active = False
            if self.level == len(PRIZE_LADDER):
                self.status = Status.WON
            return AnswerResult(True, correct_index, reached_safe_level=reached_safe)
        if self.double_dip_active and self.double_dip_first_guess is None:
            self.double_dip_first_guess = index
            return AnswerResult(False, correct_index, second_chance=True)
        self.status = Status.LOST
        self.current = None
        self.double_dip_active = False
        return AnswerResult(False, correct_index)

    def quit(self) -> int:
        self._require_playing()
        if not self.can_quit:
            raise GameRuleError("you cannot quit after taking Double Dip")
        self.status = Status.QUIT
        self.current = None
        return self.final_winnings

    @property
    def final_winnings(self) -> int:
        if self.status is Status.LOST:
            return self.guaranteed
        return self.winnings

    # ---- lifelines -----------------------------------------------------
    def _take(self, lifeline: Lifeline) -> None:
        self._require_question()
        if lifeline not in self.lifelines:
            raise GameRuleError(f"{lifeline.value} has already been used")
        if lifeline not in self.available_lifelines():
            raise GameRuleError(f"{lifeline.value} cannot be used right now")
        self.lifelines.discard(lifeline)
        self.used_this_question.add(lifeline)

    def use_fifty_fifty(self) -> list[int]:
        """Remove two wrong options; returns the indexes still visible."""
        self._take(Lifeline.FIFTY_FIFTY)
        wrong = [i for i in self.visible_options if i != self.current.answer]
        keep = self.rng.choice(wrong)
        self.hidden |= {i for i in wrong if i != keep}
        return self.visible_options

    def use_audience_poll(self) -> dict[int, int]:
        """Return a simulated poll: option index -> percentage (sums to 100).

        The audience is very reliable on easy questions and less so on hard ones.
        """
        self._take(Lifeline.AUDIENCE_POLL)
        return simulate_poll(self.current.answer, self.visible_options,
                             difficulty_for_level(self.level), self.rng)

    def use_double_dip(self) -> None:
        """Allow two guesses on this question; no quitting or other lifelines."""
        self._take(Lifeline.DOUBLE_DIP)
        self.double_dip_active = True

    def use_flip(self) -> Question:
        """Swap the current question for another one of the same level."""
        self._take(Lifeline.FLIP)
        used = self.used_this_question
        new_q = self.next_question()
        self.used_this_question = used
        return new_q

    # ---- helpers -------------------------------------------------------
    def _require_playing(self) -> None:
        if self.status is not Status.PLAYING:
            raise GameRuleError("the game is over")

    def _require_question(self) -> None:
        self._require_playing()
        if self.current is None:
            raise GameRuleError("no question is in play")


def simulate_poll(correct: int, visible: list[int], difficulty: str,
                  rng: random.Random) -> dict[int, int]:
    """Build a believable audience poll over the visible options."""
    lo, hi = {"easy": (60, 90), "medium": (40, 70), "hard": (25, 55)}[difficulty]
    correct_share = rng.randint(lo, hi)
    # Occasionally on hard questions the crowd gets it wrong.
    others = [i for i in visible if i != correct]
    if difficulty == "hard" and others and rng.random() < 0.15:
        correct_share = rng.randint(10, 30)
    remaining = 100 - correct_share
    weights = [rng.random() + 0.05 for _ in others]
    total = sum(weights) or 1
    shares = [int(remaining * w / total) for w in weights]
    if others:
        shares[0] += remaining - sum(shares)
    else:
        correct_share = 100
    poll = {correct: correct_share}
    poll.update(dict(zip(others, shares)))
    return {i: poll[i] for i in sorted(poll)}

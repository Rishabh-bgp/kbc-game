"""Terminal front end for the KBC game."""

from __future__ import annotations

import argparse
import os
import random
import sys
from typing import Callable, TextIO

from . import __version__
from .game import (PRIZE_LADDER, SAFE_LEVELS, Game, GameRuleError, Lifeline,
                   NotEnoughQuestions, Status, format_inr)
from .questions import DEFAULT_BANK, LETTERS, QuestionBankError, load_questions

LIFELINE_KEYS = {
    "1": Lifeline.AUDIENCE_POLL,
    "2": Lifeline.FIFTY_FIFTY,
    "3": Lifeline.DOUBLE_DIP,
    "4": Lifeline.FLIP,
}


class Colours:
    """ANSI colours, switched off when output is not a terminal or NO_COLOR is set."""

    CODES = {"bold": "1", "dim": "2", "red": "31", "green": "32",
             "yellow": "33", "blue": "34", "magenta": "35", "cyan": "36"}

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled
        if enabled and os.name == "nt":
            os.system("")  # enables ANSI escape handling on Windows 10+ terminals

    def __call__(self, text: str, *styles: str) -> str:
        if not self.enabled or not styles:
            return text
        codes = ";".join(self.CODES[s] for s in styles)
        return f"\033[{codes}m{text}\033[0m"


class EndOfInput(Exception):
    pass


class GameUI:
    def __init__(self, game: Game, input_fn: Callable[[str], str] = input,
                 out: TextIO = sys.stdout, colour: bool = False) -> None:
        self.game = game
        self._input = input_fn
        self.out = out
        self.c = Colours(colour)

    # ---- small I/O helpers ------------------------------------------------
    def say(self, text: str = "") -> None:
        print(text, file=self.out)

    def ask(self, prompt: str) -> str:
        try:
            return self._input(prompt).strip()
        except EOFError:
            raise EndOfInput from None

    # ---- screens ----------------------------------------------------------
    def banner(self) -> None:
        line = "=" * 54
        self.say(self.c(line, "magenta"))
        self.say(self.c("        KAUN BANEGA CROREPATI  -  Terminal Edition", "bold", "yellow"))
        self.say(self.c(line, "magenta"))

    def rules(self) -> None:
        self.say(self.c("Rules", "bold"))
        self.say(f"  * Answer {len(PRIZE_LADDER)} questions to win "
                 f"{format_inr(PRIZE_LADDER[-1])}.")
        safe = " and ".join(format_inr(PRIZE_LADDER[i]) for i in SAFE_LEVELS)
        self.say(f"  * Safe levels: {safe}. A wrong answer drops you to the last one you passed.")
        self.say("  * Lifelines (each once): Audience Poll, 50:50, Double Dip, Flip the Question.")
        self.say("  * Double Dip gives two guesses, but you can't quit or use another")
        self.say("    lifeline after taking it, and it can't follow another lifeline.")
        self.say("  * Type A-D to answer, L for a lifeline, Q to quit with your winnings.")
        self.say()

    def ladder(self) -> None:
        self.say(self.c("Prize ladder", "bold"))
        for i in reversed(range(len(PRIZE_LADDER))):
            mark = "  <- safe" if i in SAFE_LEVELS else ""
            pointer = ">" if i == self.game.level else " "
            text = f" {pointer} {i + 1:>2}. {format_inr(PRIZE_LADDER[i]):>14}{mark}"
            style = ("yellow", "bold") if i == self.game.level else (
                ("cyan",) if i in SAFE_LEVELS else ("dim",))
            self.say(self.c(text, *style))
        self.say()

    def show_question(self) -> None:
        g, q = self.game, self.game.current
        self.say()
        self.say(self.c(f"Question {g.level + 1} for {format_inr(g.prize_for_current)}",
                        "bold", "blue"))
        self.say(f"  {q.text}")
        for i in range(4):
            if i in g.hidden:
                self.say(self.c(f"    {LETTERS[i]}. ---", "dim"))
            else:
                self.say(f"    {self.c(LETTERS[i], 'yellow')}. {q.options[i]}")
        left = ", ".join(l.value for l in Lifeline if l in g.lifelines) or "none"
        self.say(self.c(f"  Banked: {format_inr(g.winnings)} | Guaranteed: "
                        f"{format_inr(g.guaranteed)} | Lifelines left: {left}", "dim"))

    def show_poll(self, poll: dict[int, int]) -> None:
        self.say(self.c("  Audience Poll:", "bold"))
        for idx, pct in poll.items():
            bar = ("#" * round(pct / 4)).ljust(25)
            self.say(f"    {LETTERS[idx]}: {self.c(bar, 'green')} {pct:>3}%")

    # ---- prompts ----------------------------------------------------------
    def choose_lifeline(self) -> None:
        g = self.game
        usable = g.available_lifelines()
        if not usable:
            reason = ("No more lifelines with Double Dip active."
                      if g.double_dip_active else "No lifelines available right now.")
            self.say(self.c(f"  {reason}", "red"))
            return
        self.say("  Lifelines:")
        for key, lifeline in LIFELINE_KEYS.items():
            if lifeline in usable:
                self.say(f"    {key}. {lifeline.value}")
        while True:
            choice = self.ask("  Pick a lifeline number (or press Enter to go back): ")
            if choice == "":
                return
            lifeline = LIFELINE_KEYS.get(choice)
            if lifeline not in usable:
                self.say(self.c("  Please pick one of the numbers shown.", "red"))
                continue
            break
        if lifeline is Lifeline.FIFTY_FIFTY:
            g.use_fifty_fifty()
            self.say(self.c("  Two wrong answers have been removed.", "green"))
        elif lifeline is Lifeline.AUDIENCE_POLL:
            self.show_poll(g.use_audience_poll())
            return  # keep the poll on screen right above the prompt
        elif lifeline is Lifeline.DOUBLE_DIP:
            g.use_double_dip()
            self.say(self.c("  Double Dip on: you get two guesses. No quitting now!", "green"))
        elif lifeline is Lifeline.FLIP:
            g.use_flip()
            self.say(self.c("  Here's a new question for the same prize.", "green"))
        self.show_question()

    def play_question(self) -> None:
        g = self.game
        g.next_question()
        self.show_question()
        while g.status is Status.PLAYING and g.current is not None:
            options = "/".join(LETTERS[i] for i in g.visible_options)
            extras = []
            if g.available_lifelines():
                extras.append("L=lifeline")
            if g.can_quit:
                extras.append("Q=quit")
            hint = f"{options}" + (f", {', '.join(extras)}" if extras else "")
            raw = self.ask(f"  Your answer ({hint}): ").upper()
            if raw in ("L", "9"):
                self.choose_lifeline()
                continue
            if raw in ("Q", "0"):
                if g.can_quit:
                    won = g.quit()
                    self.say(self.c(f"  You walk away with {format_inr(won)}.", "yellow"))
                else:
                    self.say(self.c("  You can't quit after taking Double Dip.", "red"))
                continue
            index = LETTERS.find(raw) if len(raw) == 1 and raw in LETTERS else (
                int(raw) - 1 if raw in ("1", "2", "3", "4") else -1)
            if index < 0:
                self.say(self.c("  Please type a valid option.", "red"))
                continue
            last_q = g.current
            try:
                result = g.answer(index)
            except GameRuleError as exc:
                self.say(self.c(f"  {exc}.", "red"))
                continue
            if result.correct:
                self.say(self.c(f"  Correct! You've won {format_inr(g.winnings)}.",
                                "bold", "green"))
                if result.reached_safe_level:
                    self.say(self.c("  You've reached a safe level, that money is yours!",
                                    "cyan"))
            elif result.second_chance:
                self.say(self.c("  Not that one, but Double Dip gives you one more try.",
                                "yellow"))
            else:
                q_answer = f"{LETTERS[result.correct_index]}. {last_q.options[result.correct_index]}"
                self.say(self.c("  Sorry, that's wrong.", "bold", "red")
                         + f" The correct answer was {q_answer}.")

    def run(self, name: str | None = None) -> int:
        self.banner()
        if name is None:
            name = self.ask("Enter your name: ") or "Player"
        self.say(f"Welcome to the hot seat, {self.c(name, 'bold')}!")
        self.say()
        self.rules()
        self.ladder()
        try:
            while self.game.status is Status.PLAYING:
                self.play_question()
        except NotEnoughQuestions as exc:
            self.say(self.c(f"  {exc}; ending the game.", "red"))
            if self.game.status is Status.PLAYING:
                self.game.status = Status.QUIT
        g = self.game
        self.say()
        if g.status is Status.WON:
            self.say(self.c(f"  CONGRATULATIONS {name}! You are a CROREPATI! "
                            f"You win {format_inr(g.final_winnings)}!", "bold", "yellow"))
        else:
            self.say(self.c(f"  Thanks for playing, {name}. You take home "
                            f"{format_inr(g.final_winnings)}.", "bold"))
        return g.final_winnings


def _echo_input(prompt: str) -> str:
    """Echo piped answers so transcripts of scripted games stay readable."""
    value = input(prompt)
    print(value)
    return value


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kbc", description="Play Kaun Banega Crorepati in your terminal.")
    p.add_argument("--questions", default=str(DEFAULT_BANK),
                   help="path to a JSON question bank (default: bundled bank)")
    p.add_argument("--seed", type=int, help="random seed for a repeatable game")
    p.add_argument("--name", help="player name (skips the name prompt)")
    p.add_argument("--no-color", action="store_true", help="disable coloured output")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        questions = load_questions(args.questions)
    except (OSError, QuestionBankError) as exc:
        print(f"Could not load questions: {exc}", file=sys.stderr)
        return 2
    colour = (not args.no_color and "NO_COLOR" not in os.environ
              and sys.stdout.isatty())
    game = Game(questions, rng=random.Random(args.seed))
    ui = GameUI(game, input_fn=input if sys.stdin.isatty() else _echo_input,
                colour=colour)
    try:
        ui.run(args.name)
    except (EndOfInput, KeyboardInterrupt):
        print("\nGame interrupted. Goodbye!")
        return 1
    return 0

import io
import json
import random
import tempfile
import unittest
from pathlib import Path

from kbc.cli import GameUI
from kbc.game import (PRIZE_LADDER, Game, GameRuleError, Lifeline, Status,
                      difficulty_for_level, format_inr, simulate_poll)
from kbc.questions import (Question, QuestionBankError, load_questions,
                           parse_question)


def make_bank(per_level=8):
    qs = []
    for diff in ("easy", "medium", "hard"):
        for i in range(per_level):
            qs.append(Question(f"{diff} q{i}?", ("w1", "w2", "w3", "right"), 3, diff))
    return qs


def new_game(seed=0):
    return Game(make_bank(), rng=random.Random(seed))


class FormatTests(unittest.TestCase):
    def test_indian_grouping(self):
        self.assertEqual(format_inr(0), "₹0")
        self.assertEqual(format_inr(999), "₹999")
        self.assertEqual(format_inr(10_000), "₹10,000")
        self.assertEqual(format_inr(3_20_000), "₹3,20,000")
        self.assertEqual(format_inr(7_00_00_000), "₹7,00,00,000")

    def test_ladder_shape(self):
        self.assertEqual(len(PRIZE_LADDER), 16)
        self.assertEqual(PRIZE_LADDER, sorted(PRIZE_LADDER))
        self.assertEqual(PRIZE_LADDER[-1], 7_00_00_000)

    def test_difficulty_bands(self):
        self.assertEqual([difficulty_for_level(i) for i in (0, 4, 5, 9, 10, 15)],
                         ["easy", "easy", "medium", "medium", "hard", "hard"])


class GameFlowTests(unittest.TestCase):
    def test_win_all_sixteen(self):
        g = new_game()
        seen = set()
        while g.status is Status.PLAYING:
            q = g.next_question()
            self.assertNotIn(q.text, seen, "questions must not repeat")
            seen.add(q.text)
            self.assertTrue(g.answer(q.answer).correct)
        self.assertIs(g.status, Status.WON)
        self.assertEqual(g.final_winnings, 7_00_00_000)

    def test_wrong_answer_before_first_safe_level_gives_zero(self):
        g = new_game()
        for _ in range(3):
            g.answer(g.next_question().answer)
        g.next_question()
        self.assertFalse(g.answer(0).correct)
        self.assertIs(g.status, Status.LOST)
        self.assertEqual(g.final_winnings, 0)

    def test_wrong_answer_falls_back_to_safe_levels(self):
        for answered, expected in ((5, 10_000), (9, 10_000), (10, 3_20_000), (15, 3_20_000)):
            g = new_game()
            for _ in range(answered):
                g.answer(g.next_question().answer)
            g.next_question()
            g.answer(0)
            self.assertEqual(g.final_winnings, expected, f"after {answered} correct")

    def test_quit_keeps_banked_winnings(self):
        g = new_game()
        for _ in range(7):
            g.answer(g.next_question().answer)
        g.next_question()
        self.assertEqual(g.quit(), 40_000)
        self.assertIs(g.status, Status.QUIT)

    def test_safe_level_flag(self):
        g = new_game()
        flags = []
        for _ in range(10):
            flags.append(g.answer(g.next_question().answer).reached_safe_level)
        self.assertEqual([i for i, f in enumerate(flags) if f], [4, 9])


class LifelineTests(unittest.TestCase):
    def test_fifty_fifty_keeps_answer_and_one_wrong(self):
        g = new_game()
        q = g.next_question()
        visible = g.use_fifty_fifty()
        self.assertEqual(len(visible), 2)
        self.assertIn(q.answer, visible)
        with self.assertRaises(GameRuleError):
            g.answer(next(i for i in range(4) if i not in visible))

    def test_lifelines_are_single_use(self):
        g = new_game()
        g.next_question()
        g.use_fifty_fifty()
        g.answer(3)
        g.next_question()
        with self.assertRaises(GameRuleError):
            g.use_fifty_fifty()

    def test_audience_poll_sums_to_100(self):
        for seed in range(50):
            for diff in ("easy", "medium", "hard"):
                poll = simulate_poll(2, [0, 1, 2, 3], diff, random.Random(seed))
                self.assertEqual(sum(poll.values()), 100)
                self.assertTrue(all(v >= 0 for v in poll.values()))

    def test_poll_after_fifty_fifty_only_covers_visible(self):
        g = new_game()
        g.next_question()
        visible = g.use_fifty_fifty()
        poll = g.use_audience_poll()
        self.assertEqual(sorted(poll), visible)

    def test_double_dip_gives_second_guess_and_blocks_quit(self):
        g = new_game()
        g.next_question()
        g.use_double_dip()
        self.assertFalse(g.can_quit)
        self.assertEqual(g.available_lifelines(), [])
        with self.assertRaises(GameRuleError):
            g.quit()
        first = g.answer(0)
        self.assertTrue(first.second_chance)
        with self.assertRaises(GameRuleError):
            g.answer(0)  # same option twice
        self.assertTrue(g.answer(3).correct)
        self.assertTrue(g.can_quit)

    def test_double_dip_two_wrong_loses(self):
        g = new_game()
        g.next_question()
        g.use_double_dip()
        g.answer(0)
        self.assertFalse(g.answer(1).correct)
        self.assertIs(g.status, Status.LOST)

    def test_double_dip_not_after_other_lifeline(self):
        g = new_game()
        g.next_question()
        g.use_audience_poll()
        self.assertNotIn(Lifeline.DOUBLE_DIP, g.available_lifelines())
        with self.assertRaises(GameRuleError):
            g.use_double_dip()

    def test_flip_changes_question_same_level(self):
        g = new_game()
        q1 = g.next_question()
        q2 = g.use_flip()
        self.assertNotEqual(q1.text, q2.text)
        self.assertEqual(q2.difficulty, "easy")
        self.assertEqual(g.level, 0)
        self.assertNotIn(Lifeline.FLIP, g.lifelines)


class QuestionBankTests(unittest.TestCase):
    def test_bundled_bank_is_valid_and_big_enough(self):
        qs = load_questions()
        counts = {d: sum(q.difficulty == d for q in qs) for d in ("easy", "medium", "hard")}
        # 5 easy, 5 medium, 6 hard levels, plus one spare each for Flip.
        self.assertGreaterEqual(counts["easy"], 6)
        self.assertGreaterEqual(counts["medium"], 6)
        self.assertGreaterEqual(counts["hard"], 7)
        self.assertEqual(len({q.text for q in qs}), len(qs))

    def test_rejects_bad_entries(self):
        good = {"question": "Q?", "options": ["a", "b", "c", "d"], "answer": 1}
        parse_question(good)
        for bad in ({**good, "answer": 4}, {**good, "options": ["a", "b"]},
                    {**good, "difficulty": "insane"}, {"question": "Q?"},
                    {**good, "options": ["a", "a", "c", "d"]}, {**good, "answer": True}):
            with self.assertRaises(QuestionBankError):
                parse_question(bad)

    def test_load_custom_file(self):
        data = {"questions": [{"question": "2+2?", "options": ["3", "4", "5", "6"],
                               "answer": 1, "difficulty": "easy"}]}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bank.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            qs = load_questions(path)
        self.assertEqual(qs[0].answer_text, "4")


class CliTests(unittest.TestCase):
    def run_ui(self, answers, seed=0):
        feed = iter(answers)
        out = io.StringIO()
        g = new_game(seed)
        ui = GameUI(g, input_fn=lambda _p: next(feed), out=out)
        ui.run("Tester")
        return g, out.getvalue()

    def test_invalid_input_is_rejected_then_quit(self):
        g, text = self.run_ui(["hello", "7", "", "Q"])
        self.assertIn("Please type a valid option", text)
        self.assertIs(g.status, Status.QUIT)
        self.assertIn("take home ₹0", text)

    def test_full_correct_run_through_ui(self):
        g, text = self.run_ui(["D"] * 16)
        self.assertIs(g.status, Status.WON)
        self.assertIn("CROREPATI", text)

    def test_lifeline_menu_and_wrong_answer(self):
        g, text = self.run_ui(["D", "L", "2", "A", "B", "C", "D"])
        # 1st correct; 50:50 on 2nd hides two of A/B/C; then a wrong guess ends the game.
        self.assertIn("Two wrong answers have been removed", text)
        self.assertIs(g.status, Status.LOST)
        self.assertIn("take home ₹0", text)


if __name__ == "__main__":
    unittest.main()

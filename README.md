# 🎬 KBC Game: Kaun Banega Crorepati in your terminal

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)](CONTRIBUTING.md)

A command-line quiz game based on the TV show *Kaun Banega Crorepati*. Answer 16
questions in a row to climb the prize ladder from ₹1,000 to **₹7 crore**, with four
lifelines and two safe levels to help you on the way.

This is a **free and open-source** project under the [MIT License](LICENSE).
Pull requests, new questions and ideas are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## ✨ Features

- **16-question prize ladder** from ₹1,000 to ₹7,00,00,000, with Indian-style number formatting
- **Two safe levels** at ₹10,000 and ₹3,20,000. A wrong answer drops you back to the last one you passed
- **Four lifelines**, each usable once:
  - 📊 **Audience Poll**: a simulated poll shown as a text bar chart (the crowd is less reliable on harder questions)
  - ✂️ **50:50**: removes two wrong answers
  - 🎯 **Double Dip**: two guesses at one question (no quitting or other lifelines once it's taken)
  - 🔄 **Flip the Question**: swaps the question for a new one at the same prize
- **Quit at any time** and take your banked winnings home
- **Random questions every game**, with no repeats, getting harder as you climb (easy → medium → hard)
- **Question bank in JSON** ([`kbc/data/questions.json`](kbc/data/questions.json)), easy to extend, or load your own with `--questions`
- **Input validation**: type `A`–`D` (or `1`–`4`), `L` for a lifeline, `Q` to quit
- **Coloured output** using plain ANSI codes (turned off automatically when piped, or with `--no-color` / `NO_COLOR`)
- **Pure standard library**: nothing to install beyond Python 3.9+

## 🚀 How to run

```bash
git clone https://github.com/Rishabh-bgp/kbc-game.git
cd kbc-game
python3 play.py            # or: python3 -m kbc
```

On Windows, use `py play.py`.

### Options

```text
python3 play.py --name Rishabh        # skip the name prompt
python3 play.py --seed 42             # repeatable game (same questions and polls)
python3 play.py --questions my.json   # use your own question bank
python3 play.py --no-color            # plain output
```

## 🎮 Sample game

```text
Question 2 for ₹2,000
  Which is the national animal of India?
    A. Lion
    B. Elephant
    C. Bengal Tiger
    D. Peacock
  Banked: ₹1,000 | Guaranteed: ₹0 | Lifelines left: Audience Poll, 50:50, Double Dip, Flip the Question
  Your answer (A/B/C/D, L=lifeline, Q=quit): L
  Lifelines:
    1. Audience Poll
    2. 50:50
    3. Double Dip
    4. Flip the Question
  Pick a lifeline number (or press Enter to go back): 1
  Audience Poll:
    A: ###                        12%
    B: ###                        12%
    C: ################           64%
    D: ###                        12%
  Your answer (A/B/C/D, L=lifeline, Q=quit): C
  Correct! You've won ₹2,000.

Question 3 for ₹3,000
  Which festival is popularly called the 'Festival of Lights'?
    A. Holi
    B. Diwali
    C. Eid
    D. Pongal
  Banked: ₹2,000 | Guaranteed: ₹0 | Lifelines left: 50:50, Double Dip, Flip the Question
  Your answer (A/B/C/D, L=lifeline, Q=quit): L
  Lifelines:
    2. 50:50
    3. Double Dip
    4. Flip the Question
  Pick a lifeline number (or press Enter to go back): 2
  Two wrong answers have been removed.

Question 3 for ₹3,000
  Which festival is popularly called the 'Festival of Lights'?
    A. ---
    B. Diwali
    C. ---
    D. Pongal
  Banked: ₹2,000 | Guaranteed: ₹0 | Lifelines left: Double Dip, Flip the Question
  Your answer (B/D, L=lifeline, Q=quit): B
  Correct! You've won ₹3,000.

   ... (questions 4-5) ...

Question 6 for ₹20,000
  Which city hosted the first modern Olympic Games in 1896?
    A. Paris
    B. Athens
    C. London
    D. Rome
  Banked: ₹10,000 | Guaranteed: ₹10,000 | Lifelines left: Double Dip
  Your answer (A/B/C/D, L=lifeline, Q=quit): L
  Lifelines:
    3. Double Dip
  Pick a lifeline number (or press Enter to go back): 3
  Double Dip on: you get two guesses. No quitting now!

Question 6 for ₹20,000
  Which city hosted the first modern Olympic Games in 1896?
    A. Paris
    B. Athens
    C. London
    D. Rome
  Banked: ₹10,000 | Guaranteed: ₹10,000 | Lifelines left: none
  Your answer (A/B/C/D): Q
  You can't quit after taking Double Dip.
  Your answer (A/B/C/D): C
  Not that one, but Double Dip gives you one more try.
  Your answer (A/B/C/D): B
  Correct! You've won ₹20,000.

   ... (question 7) ...

Question 8 for ₹80,000
  Who wrote India's national anthem, 'Jana Gana Mana'?
    A. Bankim Chandra Chattopadhyay
    B. Sarojini Naidu
    C. Rabindranath Tagore
    D. Subramania Bharati
  Banked: ₹40,000 | Guaranteed: ₹10,000 | Lifelines left: none
  Your answer (A/B/C/D, Q=quit): Q
  You walk away with ₹40,000.

  Thanks for playing, Rishabh. You take home ₹40,000.
```

## 📝 Adding questions

Each entry in `kbc/data/questions.json` looks like this (`answer` is the 0-based index of the right option):

```json
{
  "difficulty": "medium",
  "question": "What is the currency of Japan?",
  "options": ["Yuan", "Won", "Yen", "Ringgit"],
  "answer": 2
}
```

Levels 1–5 use `easy` questions, 6–10 `medium` and 11–16 `hard`. Keep at least 6 easy,
6 medium and 7 hard questions so the Flip lifeline always has a spare.

## 🧪 Running the tests

```bash
python3 -m unittest discover -v     # or: pytest
```

## 📁 Project layout

```text
kbc/
  game.py        game rules: prize ladder, safe levels, lifelines (no I/O, easy to test)
  questions.py   loads and validates the JSON question bank
  cli.py         terminal interface
  data/questions.json
tests/test_game.py
play.py          launcher
```

## 🙏 Credits

Inspired by the GeeksforGeeks tutorial
[**KBC game using Python**](https://www.geeksforgeeks.org/python/kbc-game-using-python/).
This repository is an independent implementation of the same idea: the code and
question bank were written from scratch, and the audience poll uses a text chart
instead of Matplotlib so the game needs no extra libraries.

*Kaun Banega Crorepati* is a trademark of its respective owners. This is a fan-made,
non-commercial learning project and is not affiliated with the show.

## 📄 License

Released under the [MIT License](LICENSE). © 2026 Rishabh Aryan.

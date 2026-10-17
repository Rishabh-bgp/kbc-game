# Contributing to KBC Game

Thanks for your interest in improving this project! All kinds of contributions are
welcome: new questions, bug fixes, features, docs and tests.

## Getting started

1. Fork the repository and clone your fork.
2. Create a branch: `git checkout -b my-change`.
3. Make your change. The game uses only the Python standard library (3.9+).
4. Run the tests: `python3 -m unittest discover -v`.
5. Commit with a clear message and open a pull request describing what you changed and why.

## Adding questions

- Add entries to `kbc/data/questions.json` with `difficulty` (`easy`, `medium` or `hard`),
  `question`, four distinct `options`, and `answer` (the 0-based index of the correct option).
- Please double-check facts and avoid questions whose answer may change soon.
- Write your own questions; don't copy them from other quiz sites or books.
- Run the tests: they validate the whole bank.

## Ideas for contributions

- More questions, or themed question packs (science, sports, Bollywood...)
- A "Phone a Friend" or "Expert Advice" lifeline
- A countdown timer for the early questions
- A high-score file
- Hindi language support

## Reporting bugs

Open an issue with the steps to reproduce, what you expected, what happened, your OS
and your Python version. Running with `--seed N` makes a game repeatable, which helps a lot.

## Code style

- Follow PEP 8 and keep functions small.
- Keep game rules in `kbc/game.py` free of `input()`/`print()` so they stay testable.
- Add or update tests for any behaviour you change.

By contributing, you agree that your contributions will be licensed under the MIT License,
and you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

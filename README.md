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

## 🔗 Other repositories by Rishabh Aryan

| Repository | Description | Live |
|---|---|---|
| [100-days-of-python](https://github.com/Rishabh-bgp/100-days-of-python) | My original, offline, no-API-key solutions to all 100 projects of the 100 Days of Code Python bootcamp curriculum… | — |
| [Agentic-Engineering-Ebook](https://github.com/Rishabh-bgp/Agentic-Engineering-Ebook) | Agentic Engineering is a practical notebook-book on specifying, generating, verifying, and refining multi-tenant… | — |
| [beed-ml-study](https://github.com/Rishabh-bgp/beed-ml-study) | Provenance audit and leakage-aware benchmark of seizure-type classifiers on the Bangalore EEG Epilepsy Dataset — IIT… | — |
| [Brain-Computer-Interfaces-and-Cognitive-Computing-An-Introduction](https://github.com/Rishabh-bgp/Brain-Computer-Interfaces-and-Cognitive-Computing-An-Introduction) | Brain–computer interfaces (BCIs) link neural activity to external devices, translating brain signals via algorithms… | — |
| [building-a-virtual-cell-in-python](https://github.com/Rishabh-bgp/building-a-virtual-cell-in-python) | A cell has a normal gene-activity pattern. Knock out one gene and that pattern changes. This project trains a small… | — |
| [Chronic-Kidney-Disease-Stage-Identification-in-HIV-Infected-Patients-Using-Supervised-ML](https://github.com/Rishabh-bgp/Chronic-Kidney-Disease-Stage-Identification-in-HIV-Infected-Patients-Using-Supervised-ML) | ML is transforming Chronic Kidney Disease (CKD) detection in HIV patients, catching early asymptomatic stages to… | — |
| [cobratate](https://github.com/Rishabh-bgp/cobratate) | Cobratate, an esoteric imperative programming language. Tate-flavored syntax, ordinary semantics, and a Python… | [open](https://rishabh-bgp.github.io/cobratate/) |
| [coda-synth](https://github.com/Rishabh-bgp/coda-synth) | CoDA-Synth: stylometric detection of LLM-rewritten dark-web documents with sparse TF-IDF + LinearSVC. Research lab,… | [open](https://shale-ember-delta-kite.grok.me/) |
| [IIT-ROPAR-GENAI-FOUNDATIONS](https://github.com/Rishabh-bgp/IIT-ROPAR-GENAI-FOUNDATIONS) | Free open-source Generative AI foundations ebooks (2026) covering Claude, Grok, Gemini, Cursor, OpenAI and more —… | — |
| [iris-classification](https://github.com/Rishabh-bgp/iris-classification) | Iris flower classification in Python: scikit-learn model comparison, tuning and evaluation, FastAPI /predict API,… | [open](https://rishabh-bgp.github.io/iris-classification/) |
| [knn-classifier](https://github.com/Rishabh-bgp/knn-classifier) | Simple K-Nearest Neighbors classifier on the classic Iris dataset using scikit-learn. Loads data, trains the model,… | — |
| [linear-regression-model-](https://github.com/Rishabh-bgp/linear-regression-model-) | Supervised linear regression on the scikit-learn diabetes dataset. A single feature (BMI) is used to predict… | — |
| [logistic-regression](https://github.com/Rishabh-bgp/logistic-regression) | This graduate capstone applies multi-class logistic regression to the Iris dataset. It includes EDA, stratified… | — |
| [logistics-website-capstone](https://github.com/Rishabh-bgp/logistics-website-capstone) | Logistics website capstone: Kargonaut Logistics, a premium freight site mixing claymorphism, glassmorphism and… | [open](https://rishabh-bgp.github.io/logistics-website-capstone/) |
| [lovelight-leap](https://github.com/Rishabh-bgp/lovelight-leap) | 💖 Lovelight Leap: a love-themed 2D platformer in vanilla JS canvas. 4 worlds, a boss you cheer up, original… | [open](https://rishabh-bgp.github.io/lovelight-leap/) |
| [machine-learning-part-1](https://github.com/Rishabh-bgp/machine-learning-part-1) | Machine learning in Python with scikit-learn: heart disease classification and medical insurance cost regression… | — |
| [Meeting-of-Machines-Consumer-Agents-Seller-Agents-and-Hidden-Fulfilment-Risk-in-Online-Retail](https://github.com/Rishabh-bgp/Meeting-of-Machines-Consumer-Agents-Seller-Agents-and-Hidden-Fulfilment-Risk-in-Online-Retail) | Agentic commerce lets shopping and seller agents place orders without showing operational truth. This IS case argues… | — |
| [morocco-city-aware-load-forecasting](https://github.com/Rishabh-bgp/morocco-city-aware-load-forecasting) | City-aware short-term load forecasting and peak detection on high-resolution Moroccan smart-meter data (5 zones).… | — |
| [NIELIT-DATA-SCIENCE](https://github.com/Rishabh-bgp/NIELIT-DATA-SCIENCE) | Hands-on NumPy, Pandas, and Matplotlib Jupyter notebooks for the NIELIT Data Science curriculum — practical,… | — |
| [NIELIT-MACHINE-LEARNING-PROJECTS](https://github.com/Rishabh-bgp/NIELIT-MACHINE-LEARNING-PROJECTS) | Nineteen end-to-end machine learning projects: classification, regression, clustering, and recommendation, with… | — |
| [NIELIT-PYTHON-](https://github.com/Rishabh-bgp/NIELIT-PYTHON-) | Open-source Python teaching notebooks: a language reference and five capstone programs, with detailed documentation.… | — |
| [pan-cancer-classification](https://github.com/Rishabh-bgp/pan-cancer-classification) | Leakage, equivalence, conformal reliability and data efficiency on the UCI TCGA Pan-Cancer RNA-Seq dataset — IIT… | — |
| [Predicting-Hot-Events-in-the-Early-Period-through-Bayesian-Model-for-Social-Networks](https://github.com/Rishabh-bgp/Predicting-Hot-Events-in-the-Early-Period-through-Bayesian-Model-for-Social-Networks) | This notebook details the implementation and evaluation of a Bayesian perspective Early stage Event Prediction… | — |
| [prediction-as-power](https://github.com/Rishabh-bgp/prediction-as-power) | Laboratory and working paper on prediction as power in European electricity markets. A DE-like hourly simulator… | — |
| [real-estate-valuation-taiwan](https://github.com/Rishabh-bgp/real-estate-valuation-taiwan) | Taiwan real estate valuation (Xindian, New Taipei): house price per ping prediction with scikit-learn gradient… | [open](https://rishabh-bgp.github.io/real-estate-valuation-taiwan/) |
| [snakes-and-ladders](https://github.com/Rishabh-bgp/snakes-and-ladders) | 🐍🪜 Original Snakes & Ladders browser game: hand-drawn SVG snakes and ladders, 3D dice, 2-4 humans or bots, sound,… | [open](https://rishabh-bgp.github.io/snakes-and-ladders/) |
| [spam-scan](https://github.com/Rishabh-bgp/spam-scan) | Explainable spam, phishing & Indian-scam detector for SMS/email (English, Hindi, Hinglish): TF-IDF + Logistic… | [open](https://spam-scan.onrender.com) |
| [vedic-math-hybrid-kt](https://github.com/Rishabh-bgp/vedic-math-hybrid-kt) | Hybrid Vedic Math AI: rule-based sutras (Urdhva-Tiryagbhyam, Nikhilam, Yavadunam) plus RF classifier that cleans… | — |
| [wind-turbine-power-model](https://github.com/Rishabh-bgp/wind-turbine-power-model) | Single-turbine power curves + wind-farm simulation. Weibull wind stats, hourly NASA-style speed data, and… | — |
| [zoo-website-capstone](https://github.com/Rishabh-bgp/zoo-website-capstone) | Capstone project: a fictional zoo website built twice — a beginner-style simple version and a cinematic advanced… | [open](https://rishabh-bgp.github.io/zoo-website-capstone/) |

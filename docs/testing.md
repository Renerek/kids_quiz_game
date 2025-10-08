# Test Guide

This project ships with a focused test suite covering the quiz games, authentication flows, email delivery, and localization helpers. Use this guide when you need to verify changes before shipping them.

## Quick start

```bash
python manage.py test
```

Running Django's default test command exercises every test case in the repository. On the current codebase it executes roughly a hundred tests and finishes in under a minute on a modern laptop.

## Targeted runs

For faster iteration you can execute individual test case classes:

```bash
python manage.py test quiz.tests.MathQuizTests quiz.tests.FruitGameTests
```

or single test methods:

```bash
python manage.py test quiz.tests.SpellingGameTests.test_trimmed_input_is_treated_as_correct
```

## Category runner script

The repository also includes `run_tests.py`, a small helper that groups related tests. You can run all stable groups:

```bash
python run_tests.py
```

Or run just one category by passing its name:

```bash
python run_tests.py "Core Functionality"
python run_tests.py "Game Features"
```

Each category corresponds to a list of test case classes defined in the script.

## Tips

- Always run the full suite before merging to `develop` or `main`.
- The password reset tests rely on Django's in-memory email backend. You can inspect generated messages under `sent_emails/` when using the file backend locally.
- If you add new game types, add their tests under `quiz/tests.py` or create a dedicated module and include it in `run_tests.py` so it shows up in category runs.

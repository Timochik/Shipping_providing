# Contributing to Vinted Shipping Discount System

Thank you for your interest in contributing! Here are some guidelines to help you get started.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Write clear, well-documented code** following PEP8 style guidelines.
3. **Add or update tests** to cover your changes.
4. **Open a pull request** with a clear description of your changes and why they are needed.

## Adding New Rules

- All discount and pricing rules are implemented as classes in `src/rules.py` inheriting from `DiscountRule`.
- To add a new rule:
  1. Create a new class in `src/rules.py` that implements the `apply` method.
  2. Add your rule to the `rules` list in `src/__main__.py` (order matters).
  3. Add or update tests in `tests/test_main.py` to cover your rule.

## Writing and Running Tests

- All tests are in the `tests/` directory and use Python's `unittest` framework.
- To run all tests:
  ```bash
  python -m unittest discover
  ```
- Add new test cases for any new features, rules, or bug fixes.
- Test both valid and invalid/edge input cases.

## Code Style

- Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- Use descriptive variable and function names.
- Add docstrings to all public classes and functions.
- Keep functions and classes small and focused.

## Submitting Changes

- Ensure all tests pass before submitting a pull request.
- If your change is significant, update the `README.md` as needed.

Thank you for helping make this project better! 
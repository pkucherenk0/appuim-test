# test_calculator.py
# Platform-agnostic calculator spec. Runs once against Android
# (sample-apps/AndroidCalculator) and once against iOS (sample-apps/SwiftCalc)
# via the parametrized `calculator_screen` fixture (see conftest.py).
# The test bodies never mention a locator or a platform name.


def test_addition(calculator_screen):
    calculator_screen.press_digit(2)
    calculator_screen.press_operator("add")
    calculator_screen.press_digit(3)
    calculator_screen.press_equals()

    assert float(calculator_screen.read_display()) == 5


def test_clear_resets_display(calculator_screen):
    calculator_screen.press_digit(7)
    calculator_screen.press_clear()

    assert calculator_screen.read_display() == ""

"""Cross-platform Page Object for the two sample calculator apps.

Android (sample-apps/AndroidCalculator) and iOS (sample-apps/SwiftCalc) are
two unrelated open-source projects with completely different locators
(Android: android:id resource-ids, iOS: accessibilityIdentifier strings).
That's deliberate here, to mirror the common real-world case where a
product's Android and iOS apps are separate native codebases.

This class exposes ONE platform-agnostic API (press_digit, press_operator,
press_equals, press_clear, read_display) so test bodies never need to
branch on platform. Only the LOCATORS table and a couple of small quirks
(operator symbols, "empty display" representation) differ per platform.
"""
from appium.webdriver.common.appiumby import AppiumBy

ANDROID = "android"
IOS = "ios"

# Every fixed (non-digit) locator this screen needs, keyed by platform then
# by semantic name. Operator symbols genuinely differ (iOS uses "x" for
# multiply, Android uses "*") — exactly the kind of platform quirk this
# table exists to hide behind one shared name.
_LOCATORS = {
    ANDROID: {
        "add": "com.example.calculator:id/plus",
        "subtract": "com.example.calculator:id/minus",
        "multiply": "com.example.calculator:id/multiply",
        "divide": "com.example.calculator:id/divide",
        "equals": "com.example.calculator:id/equals",
        "clear": "com.example.calculator:id/clear",
        "display": "com.example.calculator:id/resultText",
        "digit_template": "com.example.calculator:id/val{}",
    },
    IOS: {
        "add": "btn-+",
        "subtract": "btn--",
        "multiply": "btn-x",
        "divide": "btn-/",
        "equals": "btn-=",
        "clear": "btn-AC",
        "display": "display",
        "digit_template": "btn-{}",
    },
}


class CalculatorScreen:
    def __init__(self, driver, platform: str):
        if platform not in (ANDROID, IOS):
            raise ValueError(f"Unsupported platform: {platform!r}")
        self.driver = driver
        self.platform = platform
        self._locators = _LOCATORS[platform]

    def press_digit(self, digit) -> None:
        locator = self._locators["digit_template"].format(digit)
        self._find(locator).click()

    def press_operator(self, name: str) -> None:
        self._find(self._locators[name]).click()

    def press_equals(self) -> None:
        self._find(self._locators["equals"]).click()

    def press_clear(self) -> None:
        self._find(self._locators["clear"]).click()

    def read_display(self) -> str:
        """Returns the display text, normalized to '' when the display is empty.

        Android's result field is an EditText with android:hint="Calculator";
        UiAutomator2 reports that hint as .text when the field is genuinely
        empty. iOS's display just returns "" directly. Callers shouldn't have
        to know either of these facts.
        """
        text = self._find(self._locators["display"]).text
        if self.platform == ANDROID and text == "Calculator":
            return ""
        return text

    def _find(self, locator_id: str):
        by = AppiumBy.ID if self.platform == ANDROID else AppiumBy.ACCESSIBILITY_ID
        return self.driver.find_element(by, locator_id)

"""Shared pytest fixtures.

`calculator_screen` is parametrized over ("android", "ios") so any test that
takes it as an argument automatically runs once per platform. Requires:
  - Appium server running (appium --use-plugins=inspector --allow-cors)
  - the relevant emulator/simulator booted (see README.md)

If a platform's device/simulator isn't reachable, that platform's test is
skipped (not failed) so you can run the suite with only one platform up.

Running in parallel (two different devices, safe to run concurrently):
    pytest -n 2 --dist=loadgroup test_calculator.py -v

Each parametrized test is auto-tagged below with an xdist_group matching its
platform, so `--dist=loadgroup` keeps all "android" tests on one worker and
all "ios" tests on another — same-device tests stay serialized (a device
can only run one Appium session at a time), while the two platforms run at
the same time. Without --dist=loadgroup, -n just splits tests across
workers arbitrarily, which can put two sessions on the same device at once
and cause flaky failures.
"""
import os

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from selenium.common.exceptions import WebDriverException

from pages.calculator_screen import ANDROID, IOS, CalculatorScreen

APPIUM_SERVER = os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")

# Local defaults match this dev machine's setup (see README.md sections 2
# and 3 for how to check yours). CI overrides all three via env vars since
# a fresh runner's device name / iOS runtime version are only known at boot
# time — see .github/workflows/ci.yml.
ANDROID_DEVICE_NAME = os.environ.get("ANDROID_DEVICE_NAME", "emulator-5554")
IOS_DEVICE_NAME = os.environ.get("IOS_DEVICE_NAME", "iPhone 17")
IOS_PLATFORM_VERSION = os.environ.get("IOS_PLATFORM_VERSION", "26.5")


def _build_options(platform: str):
    if platform == ANDROID:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = ANDROID_DEVICE_NAME
        options.app_package = "com.example.calculator"
        options.app_activity = ".MainActivity"
        options.automation_name = "UiAutomator2"
        return options

    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = IOS_DEVICE_NAME
    options.platform_version = IOS_PLATFORM_VERSION
    options.bundle_id = "com.shuddha.FouthApp"
    options.automation_name = "XCUITest"
    return options


@pytest.fixture(params=[ANDROID, IOS])
def calculator_screen(request):
    platform = request.param
    try:
        driver = webdriver.Remote(APPIUM_SERVER, options=_build_options(platform))
    except WebDriverException as exc:
        pytest.skip(f"{platform} not reachable (is the emulator/simulator booted?): {exc}")
        return  # pragma: no cover - pytest.skip already raises

    try:
        yield CalculatorScreen(driver, platform)
    finally:
        driver.quit()


def pytest_collection_modifyitems(items):
    """Tag each calculator_screen-parametrized test with its platform's
    xdist_group, so `pytest -n 2 --dist=loadgroup` runs android/ios
    concurrently while keeping same-device tests serialized on one worker.
    """
    for item in items:
        callspec = getattr(item, "callspec", None)
        platform = callspec.params.get("calculator_screen") if callspec else None
        if platform in (ANDROID, IOS):
            item.add_marker(pytest.mark.xdist_group(name=platform))

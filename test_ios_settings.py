# test_ios_settings.py
import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions

@pytest.fixture
def driver():
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = "iPhone 17"
    options.platform_version = "26.5"       # match your simulator (xcrun simctl list devices | grep Booted)
    options.bundle_id = "com.apple.Preferences"
    options.automation_name = "XCUITest"

    drv = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield drv
    drv.quit()

def test_settings_has_search(driver):
    from appium.webdriver.common.appiumby import AppiumBy
    el = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Search")
    assert el.is_displayed()
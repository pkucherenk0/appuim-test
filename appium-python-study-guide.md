# Appium + Python Mobile Testing — Step-by-Step Study Guide

Covers Android and iOS automation with Appium's Python client, from zero to a
small working test suite. Follows this workspace's venv rules: this subfolder
gets its own `.venv` (see `/Users/pk/Documents/LearningQA/CLAUDE.md`).

---

## 0. Prerequisites

| Tool | Why | Check |
|---|---|---|
| Node.js (LTS) | Appium server runs on Node | `node -v` |
| Appium server | Core automation server | `appium -v` |
| Python 3.10+ | Test scripts | `python3 --version` |
| Java JDK 11+ | Android SDK tooling needs it | `java -version` |
| Android Studio | Android SDK, emulator, `adb` | — |
| Xcode (macOS only) | iOS Simulator, `xcrun simctl` | `xcodebuild -version` |

Since you're on macOS, both Android and iOS are testable from this machine.
iOS real-device testing needs a paid Apple Developer account for code
signing; the iOS **Simulator** works with a free account.

---

## Phase 1 — Environment Setup

### 1.1 Install Appium server
```bash
npm install -g appium
appium driver install uiautomator2   # Android driver
appium driver install xcuitest       # iOS driver
appium driver doctor uiautomator2    # verify Android setup
appium driver doctor xcuitest        # verify iOS setup (macOS only)
```
`appium-doctor` flags missing SDKs, env vars, etc. Fix everything it
reports before moving on — most early Appium pain is environment, not code.

### 1.2 Android SDK setup
- Install Android Studio → SDK Manager → install an SDK Platform + Android
  Emulator + Android SDK Platform-Tools.
- Set env vars in `~/.zshrc`:
  ```bash
  export ANDROID_HOME=$HOME/Library/Android/sdk
  export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator
  ```
- Create an emulator: Android Studio → Device Manager → Create Device (e.g.
  Pixel 7, API 34).
- Verify: `adb devices` shows the running emulator once booted.

### 1.3 iOS setup (macOS only)
- Install Xcode from the App Store, then `xcode-select --install`.
- List available simulators: `xcrun simctl list devices`.
- Boot one: `xcrun simctl boot "iPhone 15"`.
- For real-device testing later you'll also need `libimobiledevice` /
  WebDriverAgent signing — skip this until Phase 5.

### 1.4 Python project setup
Per workspace rules, this subfolder owns its own venv:
```bash
cd /Users/pk/Documents/LearningQA/appium
python3 -m venv .venv
source .venv/bin/activate
pip install Appium-Python-Client pytest
pip freeze > requirements.txt
```

### 1.5 Sanity check
```bash
appium            # start the server, default http://127.0.0.1:4723
```
Leave it running in one terminal; drive tests from another.

---

## Phase 2 — Appium Fundamentals

Study these concepts before writing tests — they explain *why* the API
looks the way it does:

1. **Client–server architecture** — your Python test is a WebDriver client;
   Appium server translates commands into platform-native automation
   (UiAutomator2 for Android, XCUITest for iOS).
2. **Desired capabilities** — a dict describing what to automate
   (`platformName`, `automationName`, `deviceName`, `app`/`appPackage`,
   etc.). This is the single biggest source of setup errors — get it right
   early.
3. **Sessions** — each test starts a session (driver instance), runs
   commands against it, then quits it. One session = one app/device
   instance under test.
4. **Locator strategies** — how you find elements:
   - `resource-id` / `accessibility id` (preferred, stable)
   - `xpath` (flexible but slow/brittle — last resort)
   - Android: UiAutomator selectors (`-android uiautomator`)
   - iOS: NSPredicate / class chain (`-ios predicate string`, `-ios class chain`)
5. **Appium Inspector** — GUI tool to explore an app's element tree and
   copy locators. Install: https://github.com/appium/appium-inspector
   (download the desktop app). Point it at your running Appium server +
   capabilities to inspect a live app.

---

## Phase 3 — Your First Android Test

### 3.1 Pick a target app
Install **Android Settings app** (already on every device/emulator) for the
very first smoke test — zero setup needed.

```python
# test_android_settings.py
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

@pytest.fixture
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "emulator-5554"   # from `adb devices`
    options.app_package = "com.android.settings"
    options.app_activity = ".Settings"
    options.automation_name = "UiAutomator2"

    drv = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield drv
    drv.quit()

def test_settings_search_visible(driver):
    search = driver.find_element(AppiumBy.ID, "com.android.settings:id/search_action_bar_title")
    assert search.is_displayed()
```

Run:
```bash
pytest test_android_settings.py -v
```

### 3.2 Core interactions to practice
- `find_element` / `find_elements`
- `.click()`, `.send_keys()`, `.text`, `.clear()`
- `driver.back()`, `driver.press_keycode()` (Android hardware keys)
- Scrolling: `driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiScrollable(...)...')`
- Waits: **never use `time.sleep()`** — use `WebDriverWait` +
  `expected_conditions`, same discipline as Selenium/Playwright.
  ```python
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
  WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((AppiumBy.ID, "some_id"))
  )
  ```
- Gestures: `driver.execute_script("mobile: swipeGesture", {...})` (W3C
  Actions API for tap/swipe/long-press).

---

## Phase 4 — Your First iOS Test

### 4.1 Boot a simulator and target Apple's built-in **Settings** app.

```python
# test_ios_settings.py
import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions

@pytest.fixture
def driver():
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = "iPhone 15"
    options.platform_version = "17.5"       # match your simulator
    options.bundle_id = "com.apple.Preferences"
    options.automation_name = "XCUITest"

    drv = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield drv
    drv.quit()

def test_settings_has_search(driver):
    from appium.webdriver.common.appiumby import AppiumBy
    el = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Search")
    assert el.is_displayed()
```

### 4.2 iOS-specific notes
- iOS locators favor `AppiumBy.ACCESSIBILITY_ID` (maps to
  `accessibilityIdentifier`) and `-ios predicate string`.
- First run per simulator is slow — Appium installs **WebDriverAgent**
  (a helper app) on the simulator; subsequent runs are faster.
- `xcrun simctl` is your debugging friend: list devices, erase, reboot.

---

## Phase 5 — Cross-Platform Test Design

1. **Page Object Model (POM)** — one class per screen, platform-specific
   locators behind a shared interface. Mirrors the POM pattern you already
   use in Playwright projects — see the `qa-python-playwright` skill for the
   same discipline applied to web.
2. **Capability factories** — a function that returns Android or iOS
   options based on a `platform` parameter/env var, so the same test body
   runs on both platforms.
3. **pytest fixtures** — parametrize driver fixtures over
   `["android", "ios"]` to run one test spec against both platforms.
4. **Config-driven caps** — move device name/app path/OS version into a
   YAML/JSON/`.env` file instead of hardcoding, so CI can override them.
5. **Real devices vs simulators/emulators**:
   - Android real device: enable Developer Options → USB debugging, `adb
     devices` must list it.
   - iOS real device: needs a provisioning profile + signing team ID in
     capabilities (`xcodeOrgId`, `xcodeSigningId`) — more setup, do this
     only once simulator flows are solid.
6. **Cloud device farms** (optional, later): BrowserStack App Automate,
   Sauce Labs, LambdaTest — same Appium client code, different remote URL +
   capabilities. Useful once you need real-device coverage without owning
   the hardware.

---

## Phase 6 — Practice Progression

Work through these roughly in order; each adds a new skill:

1. **OS built-in apps** (Settings, Calculator/Contacts) — zero install,
   pure locator/interaction practice.
2. **A dedicated Appium sample app** — purpose-built with predictable
   `resource-id`s, ideal for structured exercises (see recommendations
   below).
3. **A real third-party app** (e.g. a to-do or shopping demo app) — messier
   locators, closer to real work.
4. **Your own small app** (optional) — full control over locators if you
   want to author one.

---

## Recommended Target Apps for Practice

| App | Platform | Why it's good for practice | Link |
|---|---|---|---|
| **Android Settings / Calculator / Contacts** | Android (built-in) | Zero install, always available, good for Day 1 locators | on-device |
| **Apple Settings / Calculator** | iOS (built-in) | Same, for iOS Day 1 | on-device |
| **The App-Automate "Wikipedia" sample app** | Android + iOS | Official Appium sample apps, purpose-built for automation demos, stable IDs | https://github.com/appium/appium/tree/master/packages/appium/sample-code |
| **Sauce Labs "My Demo App"** | Android + iOS | Purpose-built demo e-commerce app (login, product list, cart, checkout) with clean `resource-id`/`accessibility id`s — the most commonly used Appium learning app | https://github.com/saucelabs/my-demo-app-rn |
| **Sauce Labs "My Demo App" (native, non-RN)** | Android (.apk) + iOS (.app/.ipa) | Prebuilt binaries ready to install, same flows as above | https://github.com/saucelabs/my-demo-app-android and https://github.com/saucelabs/my-demo-app-ios |
| **ApiDemos (Android)** | Android | Google's official test app used throughout Appium's own docs/examples — huge variety of native widgets (lists, gestures, alerts, spinners) | https://github.com/appium/appium/tree/master/packages/appium/sample-code/apps (or search "ApiDemos-debug.apk") |
| **UIKitCatalog (iOS)** | iOS | Apple's sample app exercising every native UIKit control — used in Appium's own iOS docs/examples | bundled with Xcode / Appium sample apps repo |
| **The Wikipedia app** | Android + iOS | Real production app, free, stable, good "graduate" step from demo apps to real-world apps | Play Store / App Store |

**Recommendation for this study plan:** start with OS built-in apps for
Phase 3–4, then move to **Sauce Labs "My Demo App"** for Phase 5–6 — it's
the de facto standard practice app in the Appium community, has clean
locators, and exercises login/list/cart/checkout flows that map well to
POM exercises.

---

## Reference Docs

- Appium docs: https://appium.io/docs/en/latest/
- Appium Python client: https://github.com/appium/python-client
- UiAutomator2 driver capabilities: https://github.com/appium/appium-uiautomator2-driver
- XCUITest driver capabilities: https://github.com/appium/appium-xcuitest-driver
- Appium Inspector: https://github.com/appium/appium-inspector

---

## Suggested Study Timeline

| Phase | Focus | Rough time |
|---|---|---|
| 0–1 | Environment setup, verify with `appium-doctor` | 0.5–1 day |
| 2 | Fundamentals + Appium Inspector | 0.5 day |
| 3 | Android first test + interactions | 1–2 days |
| 4 | iOS first test + interactions | 1–2 days |
| 5 | POM, cross-platform fixtures, config-driven caps | 2–3 days |
| 6 | Full suite against Sauce Labs demo app (login → cart → checkout) | 3–5 days |

Track progress by checking items off as you complete them; keep this file
as a living checklist and add notes/gotchas per section as you go.

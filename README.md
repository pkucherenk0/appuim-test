# Appium + Python — Quick Start (this repo)

Day-to-day commands for this machine's existing setup. For full background
and theory, see [`appium-python-study-guide.md`](./appium-python-study-guide.md).

Already installed on this machine: Node/Appium 3.7.0, `uiautomator2` +
`xcuitest` drivers, the `inspector` plugin, Android SDK + one AVD, Xcode
simulators. This README just covers the day-to-day start/stop/connect flow.

---

## 1. Activate the venv

Every new terminal starts outside the venv — activate it first:
```bash
cd /Users/pk/Documents/LearningQA/appium
source .venv/bin/activate
```

---

## 2. Start / stop the Android emulator

**Start** (own terminal tab, leave it running — closing the tab kills it):
```bash
emulator -avd Pixel_3a_API_34_extension_level_7_arm64-v8a -no-snapshot
```
`-no-snapshot` forces a clean cold boot. Skip it for a faster boot once
you've confirmed the AVD isn't in a bad state — add it back if you ever
get a black screen / hang on boot.

**Verify it's up:**
```bash
adb devices          # should list: emulator-5554   device
adb shell getprop sys.boot_completed   # should print: 1
```

**Stop:**
```bash
adb -s emulator-5554 emu kill
```
or just quit the emulator window (Cmd+Q), or `pkill -f qemu-system-aarch64`
if it's ever hung and won't close normally.

---

## 3. Start / stop the iOS Simulator

**Start:**
```bash
xcrun simctl list devices          # find the exact device name/UDID
xcrun simctl boot "iPhone 15"      # or whichever simulator you use
open -a Simulator                  # brings the Simulator app to front
```

**Verify it's up:**
```bash
xcrun simctl list devices | grep Booted
```

**Stop:**
```bash
xcrun simctl shutdown booted
```
or Cmd+Q the Simulator app.

---

## 4. Start the Appium server

Use `--allow-cors` so the **browser-based** Inspector can connect (skip it
if you're only ever using the desktop Inspector app):
```bash
appium --use-plugins=inspector --allow-cors
```
Leave this running in its own terminal tab. Confirm it's up:
```bash
curl -s http://127.0.0.1:4723/status
```

---

## 5. Connect Appium Inspector

**Prereq:** an emulator/simulator booted (§2 or §3) **and** the Appium
server running with `--use-plugins=inspector --allow-cors` (§4).

### Browser version
1. Open **http://127.0.0.1:4723/inspector**
2. Paste capabilities for the target app — pick one below.
3. Remote Host/Port default to `127.0.0.1:4723` — leave as is.
4. Click **Start Session**.

**Android — Settings app:**
```json
{
  "platformName": "Android",
  "appium:automationName": "UiAutomator2",
  "appium:deviceName": "emulator-5554",
  "appium:appPackage": "com.android.settings",
  "appium:appActivity": ".Settings"
}
```

**iOS — Settings app:**
```json
{
  "platformName": "iOS",
  "appium:automationName": "XCUITest",
  "appium:deviceName": "iPhone 17",
  "appium:platformVersion": "26.5",
  "appium:bundleId": "com.apple.Preferences"
}
```

**iOS — SwiftCalc (our sample calculator, see §7):**
```json
{
  "platformName": "iOS",
  "appium:automationName": "XCUITest",
  "appium:deviceName": "iPhone 17",
  "appium:platformVersion": "26.5",
  "appium:bundleId": "com.shuddha.FouthApp"
}
```

**Android — AndroidCalculator (our sample calculator, see §7):**
```json
{
  "platformName": "Android",
  "appium:automationName": "UiAutomator2",
  "appium:deviceName": "emulator-5554",
  "appium:appPackage": "com.example.calculator",
  "appium:appActivity": ".MainActivity"
}
```

> `deviceName` / `platformVersion` must match whatever's actually booted —
> check with `xcrun simctl list devices | grep Booted`. If they drift out
> of sync you'll get errors like `'X.X' does not exist in the list of
> simctl SDKs` — see §9 for known error fixes.

### Desktop app version
Same capabilities JSON, but fill in Remote Host `127.0.0.1`, Port `4723`,
Path `/` in the app's connection form instead of a URL. `--allow-cors`
isn't required for the desktop app, only the browser version.

**Common error:** `Could not connect to Appium server URL...` when using
the browser version → the server wasn't started with `--allow-cors`.
Restart it (§4) with that flag.

---

## 6. Run the Python tests

With the venv active (§1), an emulator/simulator booted, and the Appium
server running (§4):
```bash
pytest -v
```
or a single file:
```bash
pytest test_ios_settings.py -v
```

---

## 7. Sample apps in this repo

**`sample-apps/SwiftCalc/`** — open-source calculator app (MIT), cloned
from https://github.com/shuddha2021/SwiftCalc, used because the iOS
Simulator has no built-in Calculator (unlike a real iPhone). Buttons/display
got explicit `accessibilityIdentifier`s added (`btn-1`, `btn-+`, `btn-AC`,
`display`, ...) so locators are stable. Bundle id: `com.shuddha.FouthApp`.

It only needs reinstalling if you erase the simulator or create a new one:
```bash
cd sample-apps/SwiftCalc
xcodebuild -project FouthApp.xcodeproj -scheme FouthApp -sdk iphonesimulator \
  -destination "id=<simulator-udid>" -derivedDataPath build CODE_SIGNING_ALLOWED=NO
xcrun simctl install booted build/Build/Products/Debug-iphonesimulator/FouthApp.app
```

Test file: [`test_ios_calculator.py`](./test_ios_calculator.py).

**`sample-apps/AndroidCalculator/`** — open-source calculator app (MIT),
cloned from https://github.com/jwt2706/AndroidCalculator, used because this
emulator's AVD image (Google APIs, no Play Store) has no Calculator
preinstalled either. Every button already ships with a proper `android:id`
in the XML layout (`val0`–`val9`, `plus`, `minus`, `multiply`, `divide`,
`equals`, `clear`, `resultText`) — no source changes needed. Package:
`com.example.calculator`, activity: `.MainActivity`.

It only needs reinstalling if you wipe the emulator or create a new AVD:
```bash
cd sample-apps/AndroidCalculator
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

> Note: the `resultText` field is an `EditText` with
> `android:hint="Calculator"`. When it's empty, UiAutomator2 reports the
> hint as `.text` — this quirk is normalized away inside the POM (§8), so
> tests never see it.

---

## 8. Cross-platform Page Object (`pages/calculator_screen.py`)

Android's `AndroidCalculator` and iOS's `SwiftCalc` are two unrelated
open-source projects with completely different locators — this was
deliberate, to mirror the common real-world case where a product's Android
and iOS apps are separate native codebases with no shared locator strings.
(The exception: React Native / Flutter apps *can* share identical locators
across platforms, but only if developers deliberately set the same
`testID`/`key` on both — worth asking your dev team on a real project.)

`CalculatorScreen` hides that difference behind one platform-agnostic API
(`press_digit`, `press_operator`, `press_equals`, `press_clear`,
`read_display`). It also normalizes platform quirks that would otherwise
leak into every test — e.g. Android's "empty display" quirk (§7) and iOS
using `x` vs Android's `*` for multiply are both resolved inside the POM,
never in test code.

`conftest.py`'s `calculator_screen` fixture is parametrized over
`["android", "ios"]`, so [`test_calculator.py`](./test_calculator.py)'s
test bodies run once per platform automatically — no platform branching,
no duplicated test files. If only one platform's device is booted, that
platform's test is skipped rather than failed.

```bash
pytest test_calculator.py -v
# ::test_addition[android], ::test_addition[ios],
# ::test_clear_resets_display[android], ::test_clear_resets_display[ios]
```

### Running Android and iOS in parallel

Android and iOS run on two separate devices, so it's safe (and much
faster) to run them concurrently:
```bash
pytest -n 2 --dist=loadgroup test_calculator.py -v
```
`conftest.py` auto-tags each parametrized test with an `xdist_group`
matching its platform, so `--dist=loadgroup` keeps same-device tests
serialized on one worker (a device can only run one Appium session at a
time) while the two platforms run at the same time on separate workers.
Plain `-n 2` without `--dist=loadgroup` can schedule two tests onto the
same device simultaneously — don't use it here, it'll intermittently fail.

---

## 9. Troubleshooting — errors we've actually hit

| Error | Cause | Fix |
|---|---|---|
| `Could not connect to Appium server URL...` (browser Inspector) | Server started without CORS | Restart server with `--allow-cors` (§4) |
| `'X.X' does not exist in the list of simctl SDKs` | `platform_version` in test/capabilities doesn't match an installed simulator runtime | `xcrun simctl list devices | grep Booted` to get the real version, update the test |
| `connect ECONNREFUSED 127.0.0.1:8100` right after a WDA build | WebDriverAgent's first launch after a fresh build is slightly slower than Appium's retry window | Just retry — WDA is now built/cached, the retry starts fast and usually connects |
| Emulator boots to a black screen and hangs (near-zero CPU use) | Stale/corrupted AVD snapshot | `pkill -9 -f qemu-system-aarch64`, then relaunch with `-no-snapshot` for a clean cold boot |
| First XCUITest session takes 2–5 minutes with no visible progress | Normal — Xcode is compiling WebDriverAgent from source on first use | Let it finish; every later run reuses the cached build and is fast |
| Android test fails with a low-level connection error, or `NoSuchElementException` for a locator that normally works | The emulator's fake Bluetooth stack crashed and threw an "Application Error: com.google.android.bluetooth" system dialog that stole focus mid-test (confirm with `adb shell dumpsys window \| grep mCurrentFocus`) | `adb shell svc bluetooth disable` — stops the crash loop for the rest of that boot session. Re-run the test after. |

---

## Daily startup order (cheat sheet)

```bash
# Terminal 1
emulator -avd Pixel_3a_API_34_extension_level_7_arm64-v8a -no-snapshot

# Terminal 2
appium --use-plugins=inspector --allow-cors

# Terminal 3
cd /Users/pk/Documents/LearningQA/appium
source .venv/bin/activate
pytest -v
```

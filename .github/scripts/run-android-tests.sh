#!/usr/bin/env bash
# Runs as a single script file, not inline YAML, deliberately: the
# reactivecircus/android-emulator-runner action's `script:` input splits
# multi-line YAML into separate `sh -c` invocations per line rather than
# running it as one continuous script — which breaks `for` loops, `source`
# (env doesn't carry to the next "line"/invocation), and backgrounding with
# `&`. Calling this file as a single `script: bash .github/scripts/run-android-tests.sh`
# line sidesteps all of that.
set -euo pipefail

adb devices
adb install -r sample-apps/AndroidCalculator/app/build/outputs/apk/debug/app-debug.apk

# Redirect Appium's own stdout/stderr to a file instead of leaving them
# inherited from this script: tests confirmed PASSING, then the whole step
# hung for the rest of the job's timeout anyway — the CI runner's log
# streaming waits for EOF on the step's output pipe, which only happens
# once every process holding it (including a still-running backgrounded
# Appium server) closes it.
appium --log appium.log > appium_stdout.log 2>&1 &
appium_pid=$!
for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:4723/status; then
    break
  fi
  sleep 2
done

source .venv/bin/activate
ANDROID_DEVICE_NAME=emulator-5554 pytest test_calculator.py -k android -v
kill "$appium_pid" 2>/dev/null || true

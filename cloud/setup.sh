#!/usr/bin/env bash
set -euo pipefail
echo 'Review and accept the Android SDK licenses below to install build dependencies.'
sdkmanager --licenses
sdkmanager 'platform-tools' 'platforms;android-34' 'build-tools;36.0.0' 'ndk;21.3.6528147'
echo 'SDK ready. Run the FTC: Run simulator task (Ctrl+Shift+B).'

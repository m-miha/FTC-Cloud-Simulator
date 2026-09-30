#!/usr/bin/env bash
set -euo pipefail
# FTCodeSim alpha.1 invokes this Windows-shaped path even on Linux.
# Allow its final drivetrain source registration to finish before Electron reads state.
sleep 1
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/AdvantageScope"
exec /opt/ftc/squashfs-root/AppRun \
  --no-sandbox --disable-dev-shm-usage --use-gl=angle --use-angle=swiftshader \
  --enable-unsafe-swiftshader "$@" \
  >>"${XDG_CONFIG_HOME:-$HOME/.config}/AdvantageScope/cloud-launch.log" 2>&1

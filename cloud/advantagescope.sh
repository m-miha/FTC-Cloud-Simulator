#!/usr/bin/env bash
set -euo pipefail
# FTCodeSim alpha.1 invokes this Windows-shaped path even on Linux.
# Allow its final drivetrain source registration to finish before Electron reads state.
sleep 1
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/AdvantageScope"
# The AppImage runtime normally provides APPDIR. We bypass that runtime when
# launching the extracted image, so AppRun needs the directory explicitly.
export APPDIR=/opt/ftc/squashfs-root
if [[ -n "${FTC_CLOUD_LAYOUT_SCRIPT:-}" ]]; then
  python3 "$FTC_CLOUD_LAYOUT_SCRIPT" --configure-layout
fi
exec "$APPDIR/AppRun" \
  --no-sandbox --disable-dev-shm-usage --use-gl=angle --use-angle=swiftshader \
  --enable-unsafe-swiftshader "$@" \
  >>"${XDG_CONFIG_HOME:-$HOME/.config}/AdvantageScope/cloud-launch.log" 2>&1

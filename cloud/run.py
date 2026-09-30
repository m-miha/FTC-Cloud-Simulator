#!/usr/bin/env python3
"""Compile the repository's JUnit simulation and run it on the cloud desktop."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "TeamCode/build/cloud/runtime.json"
EXAMPLE = "org.firstinspires.ftc.teamcode.SimulateCodeBloodedDecode"
LAUNCHER = Path("/opt/ftc/Programs/advantagescope/AdvantageScope.exe")


def stop_group(process):
    """Clean up only the session we created, including desktop child processes."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    # The parent can exit while a Driver Station or Electron child is still alive.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def run(command, **kwargs):
    process = subprocess.Popen(command, start_new_session=True, **kwargs)
    try:
        return process.wait()
    finally:
        stop_group(process)


def valid_state(folder):
    for path in sorted(folder.glob("state-*.json")):
        try:
            state = json.loads(path.read_text())
            tabs = state["hubs"][0]["state"]["tabs"]["tabs"]
            if isinstance(tabs, list) and tabs:
                return path
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            continue
    return None


def prepare_advantagescope(folder):
    folder.mkdir(parents=True, exist_ok=True)
    prefs_path = folder / "prefs.json"
    if not valid_state(folder) or not prefs_path.exists():
        print("Initializing AdvantageScope's desktop configuration…", flush=True)
        process = subprocess.Popen([str(LAUNCHER)], start_new_session=True)
        try:
            deadline = time.monotonic() + 90
            while not (valid_state(folder) and prefs_path.exists()):
                if process.poll() is not None:
                    raise RuntimeError(f"AdvantageScope exited. See {folder / 'cloud-launch.log'}")
                if time.monotonic() >= deadline:
                    raise RuntimeError("AdvantageScope did not initialize. Open port 6080 and dismiss any startup dialog, then retry.")
                time.sleep(0.5)
        finally:
            stop_group(process)
    prefs = json.loads(prefs_path.read_text())
    prefs.update(liveMode="rlog", robotAddress="127.0.0.1", rlogPort=5800,
                 field3dModeAc="low-power", field3dModeBattery="low-power",
                 field3dAntialiasing=False)
    prefs_path.write_text(json.dumps(prefs, indent=2) + "\n")


def ensure_ports_available():
    for port in (8080, 5800):
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("0.0.0.0", port))
            except OSError as error:
                raise RuntimeError(f"Port {port} is occupied. Close the previous simulator before running again.") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-only", action="store_true")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Run this launcher inside the Linux dev container / Codespace.")
    import fcntl

    if not os.environ.get("ANDROID_HOME"):
        raise RuntimeError("Android SDK missing. Open this repository in its dev container.")
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    with (RUNTIME.parent / "run.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("A simulator build/run is already active in this workspace.") from None
        if not args.compile_only:
            if not os.environ.get("DISPLAY") or not LAUNCHER.exists():
                raise RuntimeError("Cloud desktop unavailable. Reopen the repository in its dev container.")
            ensure_ports_available()
        print("Compiling TeamCode and the existing simulation example…", flush=True)
        result = run(["bash", "gradlew", "--no-daemon", "--max-workers=2", "--console=plain",
                      "-I", "cloud/simulator.init.gradle", ":TeamCode:cloudSimPrepare"], cwd=ROOT)
        if result:
            return result
        if args.compile_only:
            print("Simulation compilation passed.")
            return 0
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
        prepare_advantagescope(config_home / "AdvantageScope")
        runtime = json.loads(RUNTIME.read_text())
        java = str(Path(os.environ["JAVA_HOME"]) / "bin/java")
        properties = [f"-D{key}={value}" for key, value in runtime["systemProperties"].items()]
        print("Open the private desktop on port 6080. Select an OpMode, INIT, then START.\n"
              "In AdvantageScope: File → Connect to Simulator → RLOG Server.\n"
              "Close the Driver Station or press Ctrl+C here before editing and running again.", flush=True)
        return run([java, "-Xmx1536m", *properties, "-Djava.awt.headless=false",
                    "-cp", runtime["classpath"], "org.junit.runner.JUnitCore", EXAMPLE],
                   cwd=runtime["workingDirectory"])


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
        sys.exit(130)
    except (RuntimeError, OSError, ValueError) as error:
        print(f"FTC cloud: {error}", file=sys.stderr)
        sys.exit(1)

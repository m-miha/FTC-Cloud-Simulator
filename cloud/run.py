#!/usr/bin/env python3
"""Compile the repository's JUnit simulation and run it on the cloud desktop."""
import argparse
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import subprocess
import sys
import time
import threading
import hashlib
import io
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "TeamCode/build/cloud/runtime.json"
EXAMPLE = "org.firstinspires.ftc.teamcode.SimulateCodeBloodedDecode"
LAUNCHER = Path("/opt/ftc/Programs/advantagescope/AdvantageScope.exe")
FIELD_ID = "FTC:2026-2027 Field"
POSE_KEY = "RealOutputs/Mecanum/position ftc coords (m)"
FIELD_ASSET = "Field2d_20262027FTCFieldV1"
FIELD_SHA256 = "41215ccc90e604a80f6b8f48daf5f0a9151cdbe7a6b64f970f35773a033849c3"


def ensure_field_asset(folder):
    destination = folder / "userAssets" / FIELD_ASSET
    if (destination / "config.json").is_file() and (destination / "image.png").is_file():
        return
    url = ("https://github.com/Mechanical-Advantage/AdvantageScopeAssets/releases/"
           f"download/default-assets-v2/{FIELD_ASSET}.zip")
    print("Installing the 2026-2027 FTC 2D field…", flush=True)
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != FIELD_SHA256:
        raise RuntimeError("2026-2027 field download checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        # Copy only the two known assets; never extract arbitrary archive paths.
        content = {}
        for name in ("config.json", "image.png"):
            matches = [item for item in archive.namelist() if item.split('/')[-1] == name]
            if len(matches) != 1:
                raise RuntimeError(f"Field archive must contain exactly one {name}")
            content[name] = archive.read(matches[0])
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in content.items():
        (destination / name).write_bytes(data)


def configure_2d_layout(folder):
    # Called by the desktop wrapper AFTER FTCodeSim writes its default 3D layout.
    # Reuse our tab on subsequent runs and preserve the user's other tabs.
    paths = list(folder.glob("state-*.json"))
    updated = False
    for path in paths:
        state = json.loads(path.read_text())
        if not state.get("hubs"):
            continue
        tabs = state["hubs"][0]["state"]["tabs"]
        tab = next((item for item in tabs["tabs"] if item.get("title") == "2D FTCodeSim"), None)
        if tab is None:
            tab = {"title": "2D FTCodeSim", "controllerUUID": uuid.uuid4().hex,
                   "renderer": None, "controlsHeight": 160}
            tabs["tabs"].append(tab)
        tab.update(type=2, controller={
            "field": FIELD_ID, "orientation": 0, "size": "medium",
            "sources": [{"type": "robot", "logKey": POSE_KEY, "logType": "Pose2d",
                         "visible": True, "options": {"bumpers": ""}}]
        })
        tabs["selected"] = tabs["tabs"].index(tab)
        temporary = path.with_suffix(".cloud-tmp")
        temporary.write_text(json.dumps(state, indent=2) + "\n")
        temporary.replace(path)
        updated = True
    if not updated:
        raise RuntimeError("No initialized AdvantageScope layout to configure")


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


def run(command, auto_connect=False, **kwargs):
    process = subprocess.Popen(command, start_new_session=True, **kwargs)
    stop = threading.Event()
    connector = None
    try:
        if auto_connect:
            connector = threading.Thread(target=connect_advantagescope, args=(stop,), daemon=True)
            connector.start()
        return process.wait()
    finally:
        stop.set()
        if connector is not None:
            connector.join(timeout=8)
        stop_group(process)


def rlog_listening(net_folder=Path("/proc/net")):
    # Inspect listeners without opening (and consuming) a simulator connection.
    for name in ("tcp", "tcp6"):
        try:
            lines = (net_folder / name).read_text().splitlines()[1:]
        except FileNotFoundError:
            continue
        for line in lines:
            columns = line.split()
            if len(columns) >= 4 and columns[3] == "0A" and columns[1].endswith(":16A8"):
                return True  # 5800, LISTEN
    return False


def desktop_command(*arguments):
    return subprocess.check_output(arguments, text=True, stderr=subprocess.STDOUT, timeout=3).strip()


def scope_windows():
    windows = []
    for line in desktop_command("wmctrl", "-l").splitlines():
        columns = line.split(None, 3)
        if len(columns) == 4 and columns[3].endswith("AdvantageScope"):
            windows.append((columns[0], columns[3]))
    return windows


def connect_advantagescope(stop):
    """Invoke the verified v26.0.2 simulator shortcut once, after OpMode INIT."""
    fallback = "Use File > Connect to Simulator > RLOG Server manually."
    try:
        if not shutil.which("xdotool"):
            raise RuntimeError("xdotool is missing; install it or rebuild the container")
        while not stop.wait(0.5):
            if not rlog_listening():
                continue
            windows = scope_windows()
            if not windows:
                continue
            window, title = windows[0]
            if "127.0.0.1" in title:
                return  # Already connecting/connected; don't reset its data.
            previous = desktop_command("xdotool", "getactivewindow")
            try:
                desktop_command("xdotool", "windowactivate", "--sync", window)
                if stop.is_set():
                    return
                desktop_command("xdotool", "key", "--clearmodifiers", "ctrl+shift+k")
                deadline = time.monotonic() + 10
                while not stop.wait(0.25):
                    if any(w == window and "127.0.0.1" in title for w, title in scope_windows()):
                        print("AdvantageScope simulator connection started. You can START the OpMode.", flush=True)
                        return
                    if time.monotonic() >= deadline:
                        raise RuntimeError("AdvantageScope did not acknowledge the connection shortcut")
            finally:
                try:
                    desktop_command("xdotool", "windowactivate", previous)
                except (OSError, subprocess.SubprocessError):
                    pass  # The previous window may have closed during shutdown.
            return
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Automatic connection: {error}. {fallback}", flush=True)


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
    ensure_field_asset(folder)
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
                 field3dAntialiasing=False, coordinateSystem="automatic")
    prefs_path.write_text(json.dumps(prefs, indent=2) + "\n")


def previous_simulations():
    """Find only standalone simulator JVMs belonging to this workspace."""
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / 'cmdline').read_bytes().split(b'\0')
            if (Path(os.fsdecode(command[0])).name == 'java'
                    and b'org.junit.runner.JUnitCore' in command
                    and EXAMPLE.encode() in command
                    and (entry / 'cwd').resolve() == ROOT / 'TeamCode'):
                yield int(entry.name)
        except (OSError, IndexError):
            continue  # A process may exit while /proc is being inspected.


def restart_previous_simulation():
    pids = set(previous_simulations())
    if not pids:
        return
    print('Stopping the previous simulation before rerunning…', flush=True)
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for pid in pids.intersection(previous_simulations()):
            try:
                # run() creates a dedicated session. Never kill a shared shell group.
                if os.getpgid(pid) == pid:
                    os.killpg(pid, sig)
                else:
                    os.kill(pid, sig)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 5
        while pids.intersection(previous_simulations()):
            if time.monotonic() >= deadline:
                break
            time.sleep(0.1)
        else:
            return
    raise RuntimeError('The previous simulator could not be stopped.')


def ensure_ports_available():
    for port in (8080, 5800):
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("0.0.0.0", port))
            except OSError as error:
                raise RuntimeError(f"Port {port} is occupied by another process, not a recognized simulator "
                                   "from this workspace. Stop that process or change its port.") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--manual-connect", action="store_true", help="Disable desktop shortcut automation")
    parser.add_argument("--configure-layout", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.configure_layout:
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
        configure_2d_layout(config_home / "AdvantageScope")
        return 0
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
            if args.compile_only:
                raise RuntimeError("A simulator build/run is already active in this workspace.") from None
            restart_previous_simulation()
            # The old launcher also needs time to finish desktop cleanup.
            deadline = time.monotonic() + 15
            while True:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise RuntimeError("A simulator build/run is still active in this workspace.") from None
                    time.sleep(0.1)
        if not args.compile_only:
            if not os.environ.get("DISPLAY") or not LAUNCHER.exists():
                raise RuntimeError("Cloud desktop unavailable. Reopen the repository in its dev container.")
            restart_previous_simulation()
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
        print("Open the private desktop on port 6080. Select an OpMode and INIT.\n"
              + ("In AdvantageScope: File > Connect to Simulator > RLOG Server.\n" if args.manual_connect else
                 "AdvantageScope will connect automatically after INIT; wait for confirmation, then START.\n") +
              "Rerunning this launcher restarts the previous simulation. Press Ctrl+C to stop it.", flush=True)
        simulation_env = os.environ.copy()
        simulation_env["FTC_CLOUD_LAYOUT_SCRIPT"] = str(Path(__file__).resolve())
        return run([java, "-Xmx1536m", *properties, "-Djava.awt.headless=false",
                    "-cp", runtime["classpath"], "org.junit.runner.JUnitCore", EXAMPLE],
                   cwd=runtime["workingDirectory"], auto_connect=not args.manual_connect,
                   env=simulation_env)


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

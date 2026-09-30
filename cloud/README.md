# FTC simulator in your browser

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new)

After publishing this repository to GitHub, select it on the Codespaces creation
page. You can then replace the button URL with
`https://codespaces.new/YOUR-ACCOUNT/YOUR-REPOSITORY?quickstart=1` for a direct link.

Edit Java in the browser, run the repository's `SimulateCodeBloodedDecode` example,
and interact with the real Driver Station and AdvantageScope windows in a second
browser tab. Each learner has a separate Codespace, files, desktop, and simulation.
No local Android Studio, Java, AdvantageScope, or robot is required.

## First run

1. The repository owner must commit and push the cloud files first. Then use the
   button above (or **Code → Codespaces → Create codespace** on the desired branch).
   A GitHub account and access to this repository are required. Use a personal
   account and the smallest **2-core / 8 GB** machine to minimize cost.
2. Wait for the container build. It installs Java 21, Android command-line tools,
   AdvantageScope, and a browser-accessible desktop. Initial downloads take several minutes.
3. In the command palette, choose **Tasks: Run Task → FTC: Set up Android SDK
   (first run)**. Review and accept the SDK licenses in the terminal; the task then
   installs the SDK packages. Repeat this after a container rebuild.
4. Open [CloudDrive.java](../TeamCode/src/main/java/org/firstinspires/ftc/teamcode/cloud/CloudDrive.java).
   Change `SPEED`, or edit another OpMode under `TeamCode/src/main/java`.
5. Save, then press **Ctrl+Shift+B**, or run **FTC: Run simulator** from the task menu.
   Compiler errors appear in the terminal. The first build downloads Maven dependencies.
6. Open the **Ports** panel, find **6080**, and click its globe icon. Keep its
   visibility **Private**. Click **Connect** in noVNC; no additional desktop password
   is needed because Codespaces authenticates the private forwarded port.
7. In the Driver Station, select **Cloud Drive**, then **INIT**. Wait for the terminal
   to report **AdvantageScope simulator connection started**, then press **START**.
   The launcher connects AdvantageScope automatically and restores desktop focus.
   The selected **2D FTCodeSim** tab shows **FTC:2026-2027 Field**, using
   `RealOutputs/Mecanum/position ftc coords (m)` as its robot Pose2d source.
   The RLOG stream is available after OpMode INIT.
8. Focus the Driver Station window inside the streamed desktop. Use **W/A/S/D**
   to drive/strafe and **J/L** to turn. Browser USB gamepads are not forwarded to
   the cloud JVM; use the keyboard. Release keys before switching browser tabs.

For another edit/run cycle, STOP the OpMode, close the Driver Station window
(or press Ctrl+C in the task terminal), edit and save, then run again.
STOP alone ends the OpMode but leaves the simulator running; it does not recompile Java.
Use noVNC's scaling/fullscreen controls if the two windows do not fit.

Edits persist while the Codespace exists. Commit and push to your own branch/fork
or download your files before deleting it. Simulation recordings appear under
`TeamCode/sim-logs/`; download them from the editor's file explorer to keep them.

## Hosting and cost

This uses **GitHub Codespaces**, with one cloud machine per learner. Hosting the
repository itself needs no running server. Personal GitHub Free accounts currently
include **120 core-hours/month** (about **60 actual hours on a 2-core machine**)
and **15 GB-month of storage**. Beyond the allowance, a 2-core machine costs
**$0.18/hour**, plus **$0.07/GB-month** storage. These are GitHub's published rates,
not a guarantee of unlimited free usage; SDKs, caches, and the custom container
count toward storage. Organization accounts have different billing arrangements.

Set a short idle timeout, stop the Codespace when finished, and delete unused
Codespaces after saving your work. Stopped Codespaces still consume storage.
Without a payment method, personal usage is blocked when the free quota is exhausted.
See [GitHub's current pricing and allowances](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces).

For a class, share this repository link and have each learner create their own
Codespace. Public repository visibility permits outside users to access the source;
forks provide a place to save their own changes. This is a Colab-like cloud workflow
using a browser IDE, not a Google Colab notebook or an anonymous public execution service.

The same dev container can run on an **x86-64 Linux VM with Docker** through
VS Code Remote SSH + Dev Containers. For a team-owned server, provide separate
accounts/containers per learner and authenticated access. Do not expose the
passwordless desktop, raw VNC (5901), Driver Station (8080), or RLOG (5800) to the
public internet. Public code execution needs stronger isolation and resource limits
than a shared container. The default deployment keeps these behind Codespaces access.

## How it works

The opt-in [Gradle init script](simulator.init.gradle) compiles the existing Android
project and exports its unit-test runtime classpath. [run.py](run.py) runs the exact
JUnit simulation example in a standalone JVM, with all OpModes discoverable through
`java.class.path`. It manages one run at a time and cleans up its child processes.
Normal Android builds and your simulation test are unchanged.

FTCodeSim `v0.1.0-alpha.1` launches AdvantageScope through a hard-coded Windows-style
path even on Linux. The container sets `LOCALAPPDATA=/opt/ftc` and places a Linux
launcher at that expected path. The initial run generates AdvantageScope's state
and preferences before FTCodeSim edits them. Rendering uses software graphics;
3D frame rates depend on the machine and connection. Electron runs with `--no-sandbox`
inside the per-user container, so keep the desktop private and run trusted code only.

The existing example supplies motors **lf/rf/lr/rr** and **pinpoint**. OpModes that
require additional devices need matching simulated hardware added in
[SimulateCodeBloodedDecode.java](../TeamCode/src/test/java/org/firstinspires/ftc/teamcode/SimulateCodeBloodedDecode.java).
The whole TeamCode module compiles, so a syntax error in any Java source can block a run.

The launcher downloads the official 2026-2027 FTC 2D field with a pinned checksum.
After FTCodeSim writes its layout, the desktop wrapper selects **2D FTCodeSim**
with the FTC-coordinate position pose in meters. Existing tabs remain available.
This changes the visualization; the Java example's DECODE physics configuration
is unchanged. The launcher sets RLOG preferences, waits
for the RLOG listener after INIT, and sends AdvantageScope's **Ctrl+Shift+K**
simulator shortcut. It checks for the localhost connection title and restores
focus. Wait for this step before driving. AdvantageScope handles reconnection
after that. Use `python3 cloud/run.py --manual-connect` to disable the shortcut.
An existing Codespace needs `sudo apt-get update && sudo apt-get install -y xdotool`
after pulling this change, or a container rebuild. New container builds include it.
When updating an existing Codespace, install the current desktop wrapper with
`sudo install -m 755 cloud/advantagescope.sh /opt/ftc/Programs/advantagescope/AdvantageScope.exe`
or rebuild the container, so layout setup runs before AdvantageScope opens.

## Troubleshooting and verification

- **SDK/license error:** rerun the SDK setup task. A local Windows `local.properties`
  must not be copied into the Linux container; Codespaces clones do not include this ignored file.
- **Empty desktop:** check the build terminal for errors; windows open after compilation.
- **AdvantageScope initialization timeout:** open the desktop, dismiss startup dialogs,
  and retry. Its log is `~/.config/AdvantageScope/cloud-launch.log`.
- **No live field:** INIT an OpMode and check the terminal for automatic-connection
  errors. If necessary use **File → Connect to Simulator → RLOG Server** and select
  **2D FTCodeSim**. The connection is to cloud-local `127.0.0.1:5800`.
  On first launch AdvantageScope may need to download its field assets.
- **Port occupied:** close the previous simulation; run only one simulation per Codespace.
- **Out of memory/slow graphics:** close other tasks; try a 4-core machine (higher cost).
- **Check without opening windows:** run **FTC: Check compilation**.

Deployment acceptance check: create a fresh Codespace, accept SDK licenses, run
Cloud Drive, confirm WASD changes the robot pose in AdvantageScope, close the
Driver Station, change SPEED, and rerun. Confirm Ctrl+C closes both windows and a
second run works. This desktop interaction must be checked on the Linux host;
static checks or compilation on Windows do not validate cloud rendering.

Maintainer checks: `python3 -m unittest discover -s cloud/tests -v` checks state
readiness and preference preservation. After **FTC: Check compilation**, the
exported `TeamCode/build/cloud/runtime.json` contains the classpath for running
`java -cp '<classpath>' cloud/tests/RuntimeSmoke.java`, which checks actual OpMode
discovery and bundled simulation assets without opening windows.

References: [FTCodeSim](https://github.com/jjophoven/FTCodeSim),
[desktop-lite](https://github.com/devcontainers/features/tree/main/src/desktop-lite),
[AdvantageScope 26.0.2](https://github.com/Mechanical-Advantage/AdvantageScope/releases/tag/v26.0.2).

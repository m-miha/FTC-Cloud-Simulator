# FTC OpMode Simulation in the Cloud via Codespaces 

[![Open in GitHub Codespaces]](https://github.com/codespaces/new/michael-mih/FTC-Cloud-Simulator?quickstart=1)


## First run

1. After making the codespace, wait for the container build. It installs Java 21, Android command-line tools,
   AdvantageScope, and a browser-accessible desktop. Initial downloads take several minutes.

2. In the command palette, choose **Tasks: Run Task → FTC: Set up Android SDK
   (first run)**. Review and accept the SDK licenses in the terminal (hit y for all of them); the task then
   installs the SDK packages. This should only need to be done once for each session..
3. When ready to test your code, press **Ctrl+Shift+B**, or run **FTC: Run simulator** from the task menu.
   The first build downloads Maven dependencies and will take longer.
4. Open the **Ports** panel, find **6080**, and click its globe icon. Click **Connect** in noVNC;
5. In the Driver Station, select the desired OpMode, then **INIT**. Once the simulator is connected, press **START**.
   **In order for input to register, the driver station window must be focused**.
6. Focus the Driver Station window inside the streamed desktop. Use **W/A/S/D**
   to drive/strafe and **J/L** to turn.

For another edit/run cycle, STOP the OpMode, close the Driver Station window
(or press Ctrl+C in the task terminal), edit and save, then run again.


References: [FTCodeSim](https://github.com/jjophoven/FTCodeSim),
[desktop-lite](https://github.com/devcontainers/features/tree/main/src/desktop-lite),
[AdvantageScope 26.0.2](https://github.com/Mechanical-Advantage/AdvantageScope/releases/tag/v26.0.2).

import org.codeblooded.ftcodesim.simulator.OpModeRegister;

/** Headless check against the actual exported runtime, without starting a simulator. */
public class RuntimeSmoke {
    public static void main(String[] args) throws Exception {
        boolean found = new OpModeRegister().getOpModes().stream().anyMatch(
            opMode -> opMode.getClass().getName().equals(
                "org.firstinspires.ftc.teamcode.cloud.CloudDrive"));
        if (!found) throw new AssertionError("Cloud Drive missing from OpMode discovery");
        ClassLoader loader = RuntimeSmoke.class.getClassLoader();
        for (String resource : new String[]{"assets/DriverStationWindow-all.jar", "assets/robot-models"}) {
            if (loader.getResource(resource) == null) throw new AssertionError("Missing " + resource);
        }
        Class.forName("org.firstinspires.ftc.teamcode.SimulateCodeBloodedDecode");
        System.out.println("PASS: OpMode discovery, simulation class, Driver Station and robot assets");
    }
}

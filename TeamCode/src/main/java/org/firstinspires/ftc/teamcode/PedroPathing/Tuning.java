package org.firstinspires.ftc.teamcode.PedroPathing;

import com.pedropathing.follower.Follower;
import com.pedropathing.tuning.autotune.*;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotorSimple;
import java.util.HashSet;
import java.util.Arrays;

/** AutoTune factories shared by the robot controller and desktop simulator. */
public final class Tuning {
    private Tuning() {}

    // AutoTune 1.0.2 publishes the framework, but not the documented MecanumTuner.
    @Tuner(name = "Mecanum Procedure")
    public static Procedure mecanumTuner() {
        return new Procedure("Mecanum Procedure", "Identify drivetrain motor names and directions.") {
            @Override public void run() throws InterruptedException {
                Inputs names = inputs("Mecanum Setup", "Enter the hardware map name for each wheel.");
                Inputs.StringField fl = names.s("Front Left HardwareMap Name").withDefault("lf");
                Inputs.StringField fr = names.s("Front Right HardwareMap Name").withDefault("rf");
                Inputs.StringField bl = names.s("Back Left HardwareMap Name").withDefault("lr");
                Inputs.StringField br = names.s("Back Right HardwareMap Name").withDefault("rr");
                awaitInputs(names);
                String[] motors = {fl.get().trim(), fr.get().trim(), bl.get().trim(), br.get().trim()};
                if (new HashSet<>(Arrays.asList(motors)).size() != 4) {
                    abort("Each wheel must have a different motor name.");
                }
                String[] fields = {"frontLeft", "frontRight", "backLeft", "backRight"};
                Display.FourWheelBot.Wheel[] wheels = Display.FourWheelBot.Wheel.values();
                StringBuilder java = new StringBuilder("public static MecanumConfig drivetrainConfig = new MecanumConfig(c -> {\n");
                for (int i = 0; i < motors.length; i++) {
                    final String motorName = motors[i];
                    if (motorName.isEmpty()) abort("Motor names cannot be blank.");
                    final int wheel = i;
                    withDisplay(Display.fourWheelBot(wheels[i], false), () -> {
                        runOpMode(new TuningOpMode<Void>("Spin " + motorName,
                                "Observe this wheel, then click Stop. On a real robot, lift the wheels clear of the floor.", true) {
                            @Override protected Void runTuningOpMode() throws InterruptedException {
                                DcMotor motor = hardwareMap.get(DcMotor.class, motorName);
                                DcMotorSimple.Direction previous = motor.getDirection();
                                DcMotor.RunMode previousMode = motor.getMode();
                                try {
                                    motor.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);
                                    motor.setDirection(DcMotorSimple.Direction.FORWARD);
                                    motor.setPower(0.25);
                                    while (opModeIsActive()) sleep(20);
                                } finally {
                                    motor.setPower(0);
                                    motor.setDirection(previous);
                                    motor.setMode(previousMode);
                                }
                                return null;
                            }
                        });
                        Inputs direction = inputs("Direction: " + motorName, "Did the wheel spin in the direction shown?");
                        Inputs.Field<Boolean> correct = direction.b("Correct direction").withDefault(true);
                        awaitInputs(direction);
                        String value = correct.get() ? "FORWARD" : "REVERSE";
                        result(motorName, value);
                        java.append("    c.").append(fields[wheel]).append("Name.set(\"")
                                .append(motorName.replace("\\", "\\\\").replace("\"", "\\\""))
                                .append("\");\n    c.").append(fields[wheel])
                                .append("Direction.set(DcMotorSimple.Direction.").append(value).append(");\n");
                    });
                }
                java.append("    c.manualBrakeMode.set(true);\n});");
                code(Language.JAVA, java.toString());
            }
        };
    }

    @Tuner(name = "Driving and Localization")
    public static Procedure tests() {
        return new Procedure("Driving and Localization", "Drive with the Driver Station gamepad/keyboard and inspect the Pinpoint pose.") {
            @Override public void run() throws InterruptedException {
                runOpMode(new TuningOpMode<Void>("Driving and Localization",
                        "Use the Driver Station controls to drive. Pose is displayed in its telemetry. Click Stop when finished.", true) {
                    @Override protected Void runTuningOpMode() throws InterruptedException {
                        Follower follower = Constants.createFollower(hardwareMap);
                        try {
                            while (opModeIsActive()) {
                                follower.manual(-gamepad1.left_stick_y, -gamepad1.left_stick_x, -gamepad1.right_stick_x);
                                follower.update();
                                telemetry.addData("Pose", follower.pose());
                                telemetry.update();
                                sleep(20);
                            }
                        } finally {
                            follower.stop();
                            follower.drivetrain.stop();
                        }
                        return null;
                    }
                });
                result("Test", "Complete");
            }
        };
    }
}

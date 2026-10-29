package org.firstinspires.ftc.teamcode.PedroPathing;

import com.pedropathing.algorithm.Foresight;
import com.pedropathing.algorithm.ForesightConfig;
import com.pedropathing.controllers.Controller;
import com.pedropathing.follower.Follower;
import com.pedropathing.math.Matrix;
import com.pedropathing.math.Vector2D;
import com.pedropathing.revhub.drivetrains.Mecanum;
import com.pedropathing.revhub.drivetrains.MecanumConfig;
import com.pedropathing.revhub.localizers.PinpointConfig;
import com.pedropathing.revhub.localizers.PinpointLocalizer;
import com.qualcomm.hardware.gobilda.GoBildaPinpointDriver;
import com.qualcomm.robotcore.hardware.DcMotorSimple;
import com.qualcomm.robotcore.hardware.HardwareMap;
import org.firstinspires.ftc.robotcore.external.navigation.DistanceUnit;

public class Constants {
    public static MecanumConfig drivetrainConfig = new MecanumConfig(c -> {
        c.frontLeftName.set("lf");
        c.frontRightName.set("rf");
        c.backLeftName.set("lr");
        c.backRightName.set("rr");
        c.frontLeftDirection.set(DcMotorSimple.Direction.REVERSE);
        c.backLeftDirection.set(DcMotorSimple.Direction.REVERSE);
        c.frontRightDirection.set(DcMotorSimple.Direction.FORWARD);
        c.backRightDirection.set(DcMotorSimple.Direction.FORWARD);
        c.manualBrakeMode.set(true);
    });

    public static PinpointConfig localizerConfig = new PinpointConfig(c -> {
        c.name.set("pinpoint");
        c.xPodOffset.set(-5.0);
        c.yPodOffset.set(0.5);
        c.offsetUnits.set(DistanceUnit.INCH);
        c.podType.set(GoBildaPinpointDriver.GoBildaOdometryPods.goBILDA_4_BAR_POD);
        c.xPodDirection.set(GoBildaPinpointDriver.EncoderDirection.FORWARD);
        c.yPodDirection.set(GoBildaPinpointDriver.EncoderDirection.FORWARD);
    });

    // Simulation starting values from SimulateCodeBloodedDecode, not a physical robot tune.
    // Pedro 2 PID/path constants cannot be copied directly into Foresight.
    public static ForesightConfig createForesightConfig() {
        return new ForesightConfig(c -> {
            c.headingFeedback.set(Controller.pid(1.0, 0, 0.05));
            c.forwardTranslational.set(Controller.pid(0.1, 0, 0));
            c.strafeTranslational.set(Controller.pid(0.1, 0, 0));
            c.brake.set((target, error) -> target / 65.0);
            c.coast.set((target, error) -> target / 65.0 + error * 0.02);
            c.maxAchievableForwardVelocity.set(65.0);
            c.maxAchievableStrafeVelocity.set(65.0);
            c.naturalForwardDeceleration.set(49.0);
            c.naturalStrafeDeceleration.set(85.0);
            c.linearBrakeCoefficients.set(Matrix.diag(0.09533276, 0.09533276));
            c.quadraticBrakeCoefficients.set(Matrix.diag(0.0014846306, 0.0014846306));
            c.headingBrakeCoefficients.set(Vector2D.cartesian(0.1, 0.01));
        });
    }

    public static Follower createFollower(HardwareMap hardwareMap) {
        return new Follower(new PinpointLocalizer(hardwareMap, localizerConfig),
                new Mecanum(hardwareMap, drivetrainConfig), new Foresight(createForesightConfig()));
    }
}

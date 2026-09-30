
package org.firstinspires.ftc.teamcode.TeleOpMode;

import com.pedropathing.follower.Follower;
import com.pedropathing.geometry.Pose;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;

import org.firstinspires.ftc.teamcode.PedroPathing.Constants;

/**
 * Desktop-safe Pedro TeleOp for FTCodeSim. It intentionally avoids FullPanels,
 * which requires the Android Robot Controller event loop.
 */
@TeleOp(name = "Sim Pedro Drive", group = "FTCodeSim")
public class TeleOpModeMark1 extends OpMode {
    private Follower follower;

    @Override
    public void init() {
        follower = Constants.createFollower(hardwareMap);
        follower.setStartingPose(new Pose(72, 72, 0));
        // This initializes Pedro's tele-op vectors and its VectorCalculator pose
        // before setTeleOpDrive() is called in loop().
        follower.startTeleopDrive();
        telemetry.addLine("Pedro simulator ready");
        telemetry.update();
    }

    @Override
    public void loop() {
        follower.setTeleOpDrive(
                -gamepad1.left_stick_y,
                -gamepad1.left_stick_x,
                -gamepad1.right_stick_x,
                false
        );
        follower.update();

        Pose pose = follower.getPose();
        telemetry.addData("X (in)", pose.getX());
        telemetry.addData("Y (in)", pose.getY());
        telemetry.addData("Heading (rad)", pose.getHeading());
        telemetry.update();
    }
}

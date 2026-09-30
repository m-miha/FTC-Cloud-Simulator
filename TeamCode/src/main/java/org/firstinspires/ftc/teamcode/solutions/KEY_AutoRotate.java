package org.firstinspires.ftc.teamcode.solutions;

import com.pedropathing.follower.Follower;
import com.pedropathing.geometry.Pose;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;

import org.firstinspires.ftc.teamcode.PedroPathing.Constants;

@TeleOp(name = "KEY - Auto Rotate Exercise", group = "Iterative OpMode")

public class KEY_AutoRotate extends OpMode {

    private DcMotor leftDriveB = null;
    private DcMotor leftDriveF = null;
    private DcMotor rightDriveB = null;
    private DcMotor rightDriveF = null;

    private Follower follower;
    private final Pose targetPose = new Pose(78, 73, 0); //heading arbitrary

    private final double kP = 0.2;
    private final double kD = 0.0001;

    private double lastError;

    private double lastRuntime;



    @Override
    public void init() {
        follower = Constants.createFollower(hardwareMap);
        follower.setStartingPose(new Pose(10, 10, 0));


        leftDriveB = hardwareMap.get(DcMotor.class, "lr");
        leftDriveF = hardwareMap.get(DcMotor.class, "lf");
        rightDriveB = hardwareMap.get(DcMotor.class, "rr");
        rightDriveF = hardwareMap.get(DcMotor.class, "rf");

        leftDriveF.setDirection(DcMotor.Direction.REVERSE);
        leftDriveB.setDirection(DcMotor.Direction.REVERSE);
        rightDriveB.setDirection(DcMotor.Direction.FORWARD);
        rightDriveF.setDirection(DcMotor.Direction.FORWARD);
    }

    @Override
    public void start(){
        resetRuntime();
        lastRuntime = getRuntime();
        lastError = 0;
    }

    @Override
    public void loop() {
        follower.update();
        Pose pose = follower.getPose();

        double deltaX = targetPose.getX() - pose.getX();
        double deltaY = targetPose.getY() - pose.getY();
        double desiredAngle = Math.atan2(deltaY, deltaX);

        double error = desiredAngle - pose.getHeading();

        if (error > Math.PI) {
            error -= 2 * Math.PI;
        } else if (error < -Math.PI) {
            error += 2 * Math.PI;
        }

        double pTerm = kP * error;

        double currentRuntime = getRuntime();
        double dT = currentRuntime - lastRuntime;
        double dTerm = ((error - lastError) / dT) * kD;

        double rotate = pTerm + dTerm;
        drive(-rotate);

        lastError = error;
        lastRuntime = currentRuntime;

        telemetry.addData("X (in)", pose.getX());
        telemetry.addData("Y (in)", pose.getY());
        telemetry.addData("Heading (rad)", pose.getHeading());
        telemetry.update();

    }

    public void drive(double rotate) {
        double fieldX = gamepad1.left_stick_x;   // right on field
        double fieldY = -gamepad1.left_stick_y;  // forward on field
        double heading = follower.getPose().getHeading();


        double drive  = fieldX * Math.cos(heading)
                + fieldY * Math.sin(heading);
        double strafe = fieldX * Math.sin(heading)
                - fieldY * Math.cos(heading);

        double fLeftPow  = drive + rotate + strafe;
        double bLeftPow  = drive + rotate - strafe;
        double fRightPow = drive - rotate - strafe;
        double bRightPow = drive - rotate + strafe;


        double scale = Math.max(1.0, Math.max(
                Math.max(Math.abs(fLeftPow), Math.abs(bLeftPow)),
                Math.max(Math.abs(fRightPow), Math.abs(bRightPow))
        ));

        leftDriveF.setPower(fLeftPow / scale);
        leftDriveB.setPower(bLeftPow / scale);
        rightDriveF.setPower(fRightPow / scale);
        rightDriveB.setPower(bRightPow / scale);
    }
}

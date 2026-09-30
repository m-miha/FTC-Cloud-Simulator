package org.firstinspires.ftc.teamcode.TeleOpMode;

import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotorSimple;
import com.qualcomm.robotcore.hardware.Servo;
import com.qualcomm.robotcore.util.ElapsedTime;
import com.qualcomm.robotcore.util.Range;

@TeleOp(name = "SUPER COOL AMAZING ROBOT", group = "Iterative OpMode")
public class TeleOpMecanum extends OpMode {
    private ElapsedTime runtime = new ElapsedTime();
    private DcMotor leftDriveB = null;
    private DcMotor leftDriveF = null;
    private DcMotor rightDriveB = null;
    private DcMotor rightDriveF = null;
    double noPower = 0.0;
    double stopTime;
    double delayOn = 300;
    double deloyOff = 550;




    @Override
    public void init() {
        telemetry.addData("Big things coming... ", "Initialized");
        leftDriveB = hardwareMap.get(DcMotor.class, "left_drive_b");
        leftDriveF = hardwareMap.get(DcMotor.class, "left_drive_f");
        rightDriveB = hardwareMap.get(DcMotor.class, "right_drive_b");
        rightDriveF = hardwareMap.get(DcMotor.class, "right_drive_f");

        leftDriveF.setDirection(DcMotor.Direction.REVERSE);
        leftDriveB.setDirection(DcMotor.Direction.REVERSE);
        rightDriveB.setDirection(DcMotor.Direction.FORWARD);
        rightDriveF.setDirection(DcMotor.Direction.FORWARD);
        telemetry.addData("Big things coming... ", "Initialized");


    }

    @Override
    public void loop() {
        double leftPower;
        double rightPower;

        double drive = -gamepad1.left_stick_y;   // Y-axis for forward/back
        double turn  = gamepad1.right_stick_x;   // X-axis for rotation
        double strafe = gamepad1.left_stick_x;   // X-axis for strafing

        // Mecanum power calculation (arcade mode)
        double fLeftPow = Range.clip(drive + turn + strafe, -1, 1);
        double bLeftPow = Range.clip(drive + turn - strafe, -1, 1);
        double fRightPow = Range.clip(drive - turn - strafe, -1, 1);
        double bRightPow = Range.clip(drive - turn + strafe, -1, 1);

        // Set motor powers
        leftDriveF.setPower(fLeftPow);
        leftDriveB.setPower(bLeftPow);
        rightDriveF.setPower(fRightPow);
        rightDriveB.setPower(bRightPow);

      

    }

}

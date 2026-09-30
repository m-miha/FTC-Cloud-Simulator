package org.firstinspires.ftc.teamcode.cloud;

import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;

/** Small editable example using the hardware names in SimulateCodeBloodedDecode. */
@TeleOp(name = "Cloud Drive", group = "Cloud examples")
public class CloudDrive extends OpMode {
    private DcMotor lf, rf, lr, rr;
    // Change this, save, close the simulator, then run again.
    private static final double SPEED = 0.5;

    @Override public void init() {
        lf = hardwareMap.get(DcMotor.class, "lf");
        rf = hardwareMap.get(DcMotor.class, "rf");
        lr = hardwareMap.get(DcMotor.class, "lr");
        rr = hardwareMap.get(DcMotor.class, "rr");
        lf.setDirection(DcMotor.Direction.REVERSE);
        lr.setDirection(DcMotor.Direction.REVERSE);
    }

    @Override public void loop() {
        double forward = -gamepad1.left_stick_y;
        double strafe = gamepad1.left_stick_x;
        double turn = gamepad1.right_stick_x;
        double scale = Math.max(1, Math.abs(forward) + Math.abs(strafe) + Math.abs(turn));
        lf.setPower(SPEED * (forward + strafe + turn) / scale);
        rf.setPower(SPEED * (forward - strafe - turn) / scale);
        lr.setPower(SPEED * (forward - strafe + turn) / scale);
        rr.setPower(SPEED * (forward + strafe - turn) / scale);
        telemetry.addData("Speed", SPEED);
        telemetry.addLine("WASD: drive / strafe; J/L: turn");
        telemetry.update();
    }

    @Override public void stop() {
        lf.setPower(0);
        rf.setPower(0);
        lr.setPower(0);
        rr.setPower(0);
    }
}

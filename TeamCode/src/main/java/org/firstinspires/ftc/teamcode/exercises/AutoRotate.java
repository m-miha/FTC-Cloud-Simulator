package org.firstinspires.ftc.teamcode.exercises;

import com.pedropathing.follower.Follower;
import com.pedropathing.math.Pose;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;

import org.firstinspires.ftc.teamcode.PedroPathing.Constants;

@TeleOp(name = "Autorotate Exercise", group = "Iterative OpMode")


/**
 * WELCOME TO THE AUTO ROTATE EXERCISE!! o(╹ڡ╹ )
 * Much of this code is written for you! The parts that need completion are labeled as such
 * with TODO: like this! 0s are used as placeholders.
 * Please reach out if there's any questions.
 * @Author michael-mih on GitHub.
 * @Email mjm2442@colubmia.edu
 */

/**
 * For this exercise, you'll be implementing an autorotation system in TeleOp. In this case,
 * the robot should always be oriented towards the blue hives regardless of where the driver
 * is. This will involve doing some basic trigonometry, and a basic
 * proportional derivative controller. The derivative part is an optional challenge.
 */

public class AutoRotate extends OpMode {

    private DcMotor leftDriveB = null;
    private DcMotor leftDriveF = null;
    private DcMotor rightDriveB = null;
    private DcMotor rightDriveF = null;


    /**
     * Our Follower object tracks our rotation and heading on the field. This information is
     * represented as a Pose, which consists of an X, Y, and heading value (rotation) in radians.
     */
    private Follower follower;

    /**
     * For simplicity's sake, there will only be one pose we want to lock on to, which is the center of the two
     * blue hives listed below as targetPose. You can imagine how a more sophisticated program may track both hive sides
     * individually.
     */
    private final Pose targetPose = new Pose(78, 73, 0); //heading arbitrary

    /**
     * PID constants that we'd tune on a real robot.
     */
    private final double kP = 0.2;
    private final double kD = 0.0001;

    private double lastError;

    private double lastRuntime;



    @Override
    public void init() {
        follower = Constants.createFollower(hardwareMap);
        follower.setPose(new Pose(10, 10, 0));


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

        follower.localizer.update();
        Pose pose = follower.pose();

        /**
         * We want to ask: How far does my robot have to rotate in order to face the blue hive? In order to do this, we need to take the difference between
         * the angle our robot should be facing, and the angle our robot is currently facing.
         */

        /**
         * Finding our current heading is trivial using a method, but finding our desired heading is a little bit more work. I've drawn a diagram
         * that is hopefully of some help in the media/ folder.
    
         * If we can establish a triangle from our robot to the blue hive, we can use tangent (specifically tangent inverse) to find the angle!
         */

        // TODO: define the x and y distance between our target pose (the blue hive) and the robot. You'll need the .x() and .y() methods
        // TODO: that belong to Pose objects.
        double deltaX = 0;
        double deltaY = 0;

        //TODO: with the x and y legnths of our triangle, find what our desired angle is in order to face the blue hive.
        //TODO: you'll need Math.atan2(y, x) (an inverse tangent method)
        //TODO: which you can read about here: https://docs.oracle.com/javase/8/docs/api/java/lang/Math.html#atan2-double-double-
        double desiredAngle = 0;

        //TODO: calculate our error, the difference between our desired angle and our current heading. you'll need the .heading() method that belongs
        //TODO: to pose objects.
        double error = 0;

        /**
         * This code ensures we never rotate the long way around the unit circle to get to our angle. I can explain it more in person if there's interest.
          */
        if (error > Math.PI) {
            error -= 2 * Math.PI;
        } else if (error < -Math.PI) {
            error += 2 * Math.PI;
        }


        /**
         * Now that we know our error (the difference between our desired heading and our current heading), we need to use that error to actually apply
         * power to our motors.
         * We'll do this through a proportional derivative controller.
         *
         */
        //TODO calculate our proportional term, which is our constant kP multiplied by our error.
        double pTerm = 0;

        double dTerm;
        dTerm = 0; //this is set in case the derivative term isn't calculated later, leave as is if not doing the challenge.
        double currentRuntime = getRuntime();

        /**
         * The derivative term calculates the rate of change of our error and multiplies that with our kD constant.
         * This is commonly thought of as "predicting" based on how the error is changing in order to minimize overshooting.
         * Here's a youtube short that gives a brief rundown. This sort of thing is popular with the youth nowadays I think:
         * https://www.youtube.com/shorts/PGK-RXA8Ye8
         * In this example, our "x" is time (note the currentRuntime and lastRuntime variables) and
         * our "f(x)" is our error (note the error and lastError variables).
         * TODO: Uncomment and fill in if you want to attempt to add the Derivative term!
         * double dT =
           double dTerm = kD *
         **/


        double rotate = pTerm + dTerm;
        drive(-rotate);

        lastError = error;
        lastRuntime = currentRuntime;

        telemetry.addData("X (in)", pose.x());
        telemetry.addData("Y (in)", pose.y());
        telemetry.addData("Heading (rad)", pose.heading());
        telemetry.update();

        /**
         * Congrats! Your robot should be drivable using WASD while always facing the blue hive!
         */
    }

    /**
     * A method to drive the robot field-centric with our calculated rotation power. You shouldn't have to
     * touch this.
     * @param rotate our calculated rotation power
     */
    public void drive(double rotate) {
        double fieldX = gamepad1.left_stick_x;   // right on field
        double fieldY = -gamepad1.left_stick_y;  // forward on field
        double heading = follower.pose().heading();


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

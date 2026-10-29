package org.firstinspires.ftc.teamcode.PedroPathing.AutoCode; // make sure this aligns with class location

import com.pedropathing.follower.Follower;
import static com.pedropathing.api.Paths.*;
import com.pedropathing.ivy.behaviors.EndCondition;
import com.pedropathing.math.Pose;
import com.pedropathing.ivy.Command;
import com.pedropathing.ivy.Scheduler;
import com.pedropathing.paths.Path;
import com.qualcomm.robotcore.eventloop.opmode.Autonomous;
import com.qualcomm.robotcore.eventloop.opmode.LinearOpMode;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;

import static com.pedropathing.ivy.Scheduler.schedule;

import static com.pedropathing.ivy.groups.Groups.*;

import org.firstinspires.ftc.teamcode.PedroPathing.Constants;

public class AutoCodeMethods {


//    private Follower follower;
    public static final Pose startPose = new Pose(22, 122, Math.toRadians(324)); // Start Pose of our robot. This is against the goal facing AWAY
    private static final Pose scorePose = new Pose(60, 84, Math.toRadians(135)); // Scoring Pose of our robot.
    private static final Pose pickup1Pose = new Pose(17, 84, Math.toRadians(180)); // Highest (First Set) of Artifacts from the Spike Mark.
    private static final Pose pickup2Pose = new Pose(12, 60, Math.toRadians(180)); // Middle (Second Set) of Artifacts from the Spike Mark.
    private static final Pose pickup3Pose = new Pose(12, 36, Math.toRadians(180)); // Lowest (Third Set) of Artifacts from the Spike Mark.
    private static final Pose endPose = new Pose (60, 105); // Final Pose of our robot, off the starting line
    //defining our Paths
    private static Path scorePreload;
    private static Path grabPickup1;
    private static Path scorePickup1;
    private static Path grabPickup2;
    private static Path scorePickup2;
    private static Path grabPickup3;
    private static Path scorePickup3;
    private static Path leave;

    public static void buildPaths(Follower follower) {
        scorePreload = line(startPose, scorePose).linear(startPose.heading(), scorePose.heading());


        /* This is our grabPickup1 Path. We are using a single path with a BezierLine, which is a straight line. */
        grabPickup1 = line(scorePose, pickup1Pose).linear(scorePose.heading(), pickup1Pose.heading());

        /* This is our scorePickup1 Path. We are using a single path with a BezierLine, which is a straight line. */
        scorePickup1 = line(pickup1Pose, scorePose).linear(pickup1Pose.heading(), scorePose.heading());

        /* This is our grabPickup2 Path. We are using a single path with a BezierCurve (curved line). */
        grabPickup2 = curve(scorePose, new Pose(60, 54), pickup2Pose).linear(scorePose.heading(), pickup2Pose.heading());

        /* This is our scorePickup2 Path. We are using a single path with a BezierCurve (curved line). */
        scorePickup2 = curve(pickup2Pose, new Pose(60, 54), scorePose).linear(pickup2Pose.heading(), scorePose.heading());

        /* This is our grabPickup3 Path. We are using a single path with a BezierCurve (curved line). */
        grabPickup3 = curve(scorePose, new Pose(60, 30), pickup3Pose).linear(scorePose.heading(), pickup3Pose.heading());

        /* This is our scorePickup3 Path. We are using a single path with a BezierCurve (curved line). */
        scorePickup3 = curve(pickup3Pose,new Pose(60, 30), scorePose).linear(pickup3Pose.heading(), scorePose.heading());

        /* This is our leave Path. We are using a single path using a BezierLine (straight line).
         * We use Constant Interpolation here instead of Linear*/
        leave = line(scorePose, endPose).constant(scorePose.heading());
    }
    public static Command autoRoutine(Follower follower) {
        return sequential(
                /* Go To Score Command*/
                follow(follower, scorePreload),
                /* Collect 3 Artifacts Command*/
                follow(follower, grabPickup1, true),
                /* Go Back To Score Command*/
                follow(follower, scorePickup1, true),
                /* Collect 3 Artifacts Command*/
                follow(follower, grabPickup2, true),
                /* Go Back To Score Command*/
                follow(follower, scorePickup2, true),
                /* Collect 3 Artifacts Command*/
                follow(follower, grabPickup3, true),
                /* Go Back To Score Command*/
                follow(follower, scorePickup3, true),
                /* Leave Start Line Command*/
                follow(follower, leave, true)
        );
    }

    // Ivy 1.0's bundled PedroCommands target Pedro 2. Use its generic command API.
    private static Command follow(Follower follower, Path path) {
        return follow(follower, path, true);
    }

    private static Command follow(Follower follower, Path path, boolean holdEnd) {
        return Command.build().setStart(() -> {
            follower.holdEnd.set(holdEnd);
            follower.follow(path);
        }).setDone(() -> !follower.following() && !follower.isBusy())
          .setEnd(reason -> {
              if (reason == EndCondition.INTERRUPTED) {
                  follower.stop();
                  follower.drivetrain.stop();
              }
          });
    }
}

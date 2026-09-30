package org.firstinspires.ftc.teamcode.AutonomousOpMode;

import static com.pedropathing.ivy.Scheduler.schedule;
import static org.firstinspires.ftc.teamcode.PedroPathing.AutoCode.AutoCodeMethods.autoRoutine;
import static org.firstinspires.ftc.teamcode.PedroPathing.AutoCode.AutoCodeMethods.buildPaths;
import static org.firstinspires.ftc.teamcode.PedroPathing.AutoCode.AutoCodeMethods.startPose;
import static org.firstinspires.ftc.teamcode.PedroPathing.Tuning.follower;

import com.pedropathing.follower.Follower;
import com.pedropathing.ivy.Scheduler;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;

import org.firstinspires.ftc.teamcode.PedroPathing.Constants;
public class AutoCodeMark1 extends OpMode {

    @Override
public void init() {
    Scheduler.reset();
    Follower follower = Constants.createFollower(hardwareMap);
    buildPaths(follower);
    follower.setStartingPose(startPose);
}

    @Override
 public void start(){
    schedule(autoRoutine(follower));
 }

    @Override
 public void loop() {
     follower.update();
     Scheduler.execute();
 // Feedback to Driver Hub for debugging
     telemetry.addData("x", follower.getPose().getX());
     telemetry.addData("y", follower.getPose().getY());
     telemetry.addData("heading", follower.getPose().getHeading());
     telemetry.update();
 }
}


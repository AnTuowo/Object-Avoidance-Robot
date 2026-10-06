#!/usr/bin/env python3
import rospy
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

import argparse

class Milestone1Controller:
    def __init__(self, target_x, target_y):
        rospy.init_node('milestone1_controller', anonymous=True)

        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_callback)

        self.target_x = target_x
        self.target_y = target_y

        self.curr_x = 0.0
        self.curr_y = 0.0
        self.curr_yaw = 0.0
        self.odom_received = False

    def odom_callback(self, msg):
        self.curr_x = msg.pose.pose.position.x
        self.curr_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        _, _, self.curr_yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.odom_received = True

    def run(self):
        rate = rospy.Rate(10)
        rospy.loginfo("Waiting for /odom data from Unity...")
        
        while not rospy.is_shutdown() and not self.odom_received:
            rate.sleep()

        rospy.loginfo(f"Moving to target: X={self.target_x}, Y={self.target_y}")

        while not rospy.is_shutdown():
            # ---------------- CALCULATE DIST AND ANGLE ERROR ----------------
            dx = self.target_x - self.curr_x
            dy = self.target_y - self.curr_y
            dist = math.hypot(dx, dy)

            target_angle = math.atan2(dy, dx)
            angle_err = target_angle - self.curr_yaw

            # Normalize angle to range [-pi, pi]
            angle_err = math.atan2(math.sin(angle_err), math.cos(angle_err))

            rospy.loginfo(f"Dist: {dist:.2f} m | Yaw: {math.degrees(self.curr_yaw):.1f}° | Err: {math.degrees(angle_err):.1f}°")


            # ---------------- CONTROL BY PUBLISH TO CMD_VEL ----------------
            cmd = Twist()


            # Target reached condition (10 cm tolerance to prevent stalling near the goal)
            if dist < 0.1:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.cmd_pub.publish(cmd)
                rospy.loginfo("Milestone 1 Completed: Target reached!")
                break

            MIN_ANGULAR_VEL = 0.4
            ANGLE_THRESHOLD = math.radians(5)
            ANG_VEL_SIGN = math.copysign(1, angle_err)
            # If facing opposite direction, rotate out of the 180-degree wrap-around trap
            if abs(math.degrees(angle_err)) > 165.0:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.5 * ANG_VEL_SIGN
            elif abs(angle_err) > ANGLE_THRESHOLD:
                # Rotate toward target heading
                cmd.linear.x = 0.0
                ang_vel = max(-0.6, min(0.6, 0.8 * angle_err))
                cmd.angular.z = ang_vel if abs(ang_vel) >= MIN_ANGULAR_VEL else MIN_ANGULAR_VEL * ANG_VEL_SIGN
            else:
                cmd.linear.x = 0.8 if dist > 0.8 else min(0.8, max(0.3, 0.6 * dist))
                ang_vel = 0.6 * angle_err
                cmd.angular.z = ang_vel if abs(ang_vel) >= MIN_ANGULAR_VEL else MIN_ANGULAR_VEL * ANG_VEL_SIGN

            self.cmd_pub.publish(cmd)
            rate.sleep()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Move robot to target X/Y position'
    )

    parser.add_argument(
        'target_x',
        type=float,
        help='Target X coordinate'
    )

    parser.add_argument(
        'target_y',
        type=float,
        help='Target Y coordinate'
    )

    args = parser.parse_args()

    try:
        controller = Milestone1Controller(
            target_x=args.target_x,
            target_y=args.target_y
        )

        controller.run()

    except rospy.ROSInterruptException:
        pass

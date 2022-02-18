#!/usr/bin/env python

import rospy
import sys
import math
import tf
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from tf.transformations import euler_from_quaternion
from math import pi

# map from letter input to x linear and z angular
key_mapping = {'l': [0,-1], 'r': [0,1], 
               'f': [1,0], 'b': [-1,0],
               'h': [0,0], 's': [1,1],
               'z': [0,0], }
movement_vector = {}

# fill in scan callback
def scan_cb(msg):
   global range_ahead
   range_ahead = msg.ranges[0]

# it is not necessary to add more code here but it could be useful
def key_cb(msg):
   global state; global last_key_press_time
   state = msg.data
   last_key_press_time = rospy.Time.now()

# odom is also not necessary but very useful
def odom_cb(msg):
   global x; global y; global turn
   x = msg.pose.pose.position.x
   y = msg.pose.pose.position.y
   quater = msg.pose.pose.orientation
   (roll, pitch, turn) = euler_from_quaternion([quater.x, quater.y, quater.z, quater.w])

# print the state of the robot
def print_state():
   print('---')
   print('STATE: ' + state.upper())

   # calculate time since last key stroke
   time_since = rospy.Time.now() - last_key_press_time
   print("SECS SINCE LAST KEY PRESS: " + str(time_since.secs))

# init node
rospy.init_node('dancer')

# subscribers/publishers
scan_sub = rospy.Subscriber('scan', LaserScan, scan_cb)

# RUN rosrun prrexamples key_publisher.py to get /keys
key_sub = rospy.Subscriber('keys', String, key_cb)
odom_sub = rospy.Subscriber('odom', Odometry, odom_cb)
cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)

# start in state halted and grab the current time
state = "H"
range_ahead = 0
last_key_press_time = rospy.Time.now()

# set rate
rate = rospy.Rate(10)

print('Here are the commands: \n    l: rotate left\n    r: rotate right\n    ' +
      'f: move forward\n    b: move backward\n    h: halt all motion\n    ' +
      's: spiralling motion\n    z: zigzag motion\n    p: print state and time')

# Wait for published topics, exit on ^c
while not rospy.is_shutdown():

   # print out the current state and time since last key press
   print_state()

   # publish cmd_vel from here
   t = Twist()
   linear_speed = 0.2 # linear speed of 0.2 m/s
   angular_speed = pi/4 # angular speed of pi/4 radians/s

   # stop if robot is 0.2m away from a wall
   if range_ahead < 0.2:
      state = 'h' # linear movement and angular movement depending on key press
      t.linear.x = 0
      t.angular.z = 0
   
   # find velocity vector and move (did not manage to get this part to work)
   #if state.lower() == 'z':
   #   zig_start_time = rospy.Time.now()
   #   while(state.lower() == 'z' and range_ahead < 0.2):
   #      if(zig_start_time.secs%4 == 0):
   #         t.linear.x = linear_speed*1
   #         t.angular.z = angular_speed*0
   #      elif(zig_start_time%4 == 1):
   #         t.linear.x = linear_speed*0
   #         t.angular.z = angular_speed*1
   #      elif(zig_start_time%4 == 2):
   #         t.linear.x = linear_speed*1
   #         t.angular.z = angular_speed*0
   #      else:
   #         t.linear.x = linear_speed*0
   #         t.angular.z = angular_speed*-1
   #      cmd_vel_pub.publish(t)
   if state.lower() in key_mapping: # simple movements
      velocity_vector = key_mapping[state.lower()] # linear movement and angular movement depending on key press
      t.linear.x = linear_speed*velocity_vector[0]
      t.angular.z = angular_speed*velocity_vector[1]
      print('SPEED: ' + str(linear_speed*velocity_vector[0]))
   
   # publish the velocities
   cmd_vel_pub.publish(t)

   # run at 10hz
   rate.sleep()

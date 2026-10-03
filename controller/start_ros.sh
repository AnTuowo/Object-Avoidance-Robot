#!/bin/bash

cd ../catkin_ws
source devel/setup.bash
roslaunch ros_tcp_endpoint endpoint.launch

exec bash

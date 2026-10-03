# Object-Avoidance-Robot in Unity

## Prerequisites
- Ubuntu Linux version 20.04 LTS 

- Install Unity 2022.3 LTS 
- ROS1 Noetic
```bash
 sudo apt-get install ros-noetic-desktop-full
 sudo apt-get install ros-noetic-xacro
 sudo apt-get install ros-noetic-gazebo-ros
 ```

## Open Unity
Inside Assets > URDF > Mastering_ros_robot_description_pkg > urdf

You copy one robot from udf folder (.urdf file) to Assets > URDF.

* note: if the file ending in .xacro, you must convert it into .urdf  
```bash
rosrun xacro xacro your_robot.urdf.xacro > your_robot.urdf
```

## Set up workspace
```bash
git clone https://github.com/AnTuowo/Object-Avoidance-Robot.git
cd ~/robot-inspection-repo/catkin_ws
git submodule update --init --recursive
catkin_make
source devel/setup.bash
```
Everytime you make changes to the catkin_ws, adding packages etc..:
```bash
catkin_make
```

Everytime you open new terminal:
```bash
source devel/setup.bash
```
## Connecting ROS to Unity
Check your ip address. In terminal:
```bash
hostname -I
```
or
```bash
ip a
```

In Unity, navigate to Robotics and choose ROS settings. Then, you can change your ip address and/or port number accordinngly.

In terminal:
```bash
roslaunch ros_tcp_endpoint endpoint.launch
```
If you see something similar to ```[INFO] [1790824725.189861]: Starting server on 0.0.0.0:10000``` then it is correct.

## Control the automobile
Open new terminal:
```bash
cd ~/robot-inspection-repo/catkin_ws
source devel/setup.bash
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```
Make sure to put the terminal above the unity workspace.

Hit Play ▶️  in Unity


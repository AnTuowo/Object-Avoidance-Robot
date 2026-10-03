import math

# Pose(x, y, z, yaw_angle)
# ros_x = uni_z
# ros_y = -uni_x
# ros_z = uni_y
# ros_yaw = -uni_yaw

def unity_to_ros(x: float, y: float, z: float, yaw: float) -> tuple:
    return (z,
            -x if x is not None else None, 
            y, 
            -yaw if yaw is not None else None
            )

def ros_to_unity(x: float, y: float, z: float, yaw: float) -> tuple:
    return (-y if y is not None else None, 
            z, 
            x, 
            -yaw if yaw is not None else None
            )

def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)
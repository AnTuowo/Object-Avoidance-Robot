using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Nav;
using RosMessageTypes.Geometry;
using RosMessageTypes.Std;
using RosMessageTypes.BuiltinInterfaces;

public class OdometryPublisher : MonoBehaviour
{
    ROSConnection ros;
    public string topicName = "/odom";
    public string frameId = "odom";
    public string childFrameId = "base_footprint";

    public float publishMessageFrequency = 0.05f; // 20 Hz
    private float timeElapsed;

    // Drag base_footprint here in the Inspector, or leave empty to auto-detect
    public Transform robotTransform;
    private Vector3 initialPosition;

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<OdometryMsg>(topicName);

        if (robotTransform == null)
        {
            // Find base_footprint if attached to parent
            Transform child = transform.Find("base_footprint");
            robotTransform = child != null ? child : transform;
        }

        initialPosition = robotTransform.position;
    }

    void Update()
    {
        timeElapsed += Time.deltaTime;

        if (timeElapsed >= publishMessageFrequency)
        {
            PublishOdom();
            timeElapsed = 0;
        }
    }

    void PublishOdom()
    {
        OdometryMsg odom = new OdometryMsg();

        odom.header = new HeaderMsg
        {
            stamp = new TimeMsg
            {
                sec = (uint)Time.time,
                nanosec = (uint)((Time.time - (uint)Time.time) * 1e9)
            },
            frame_id = frameId
        };

        odom.child_frame_id = childFrameId;

        // Position relative to start (Unity left-handed -> ROS right-handed)
        Vector3 relPos = robotTransform.position - initialPosition;
        odom.pose.pose.position.x = relPos.z;
        odom.pose.pose.position.y = -relPos.x;
        odom.pose.pose.position.z = relPos.y;

        // Convert Unity euler rotation to ROS yaw
        // In Unity, rotating clockwise increases Y angle; in ROS, yaw is counter-clockwise around Z
        float unityYaw = robotTransform.eulerAngles.y;
        float rosYaw = -unityYaw * Mathf.Deg2Rad;
        // Normalize to [-pi, pi]
        rosYaw = Mathf.Atan2(Mathf.Sin(rosYaw), Mathf.Cos(rosYaw));

        // Create quaternion from yaw
        odom.pose.pose.orientation.x = 0.0;
        odom.pose.pose.orientation.y = 0.0;
        odom.pose.pose.orientation.z = Mathf.Sin(rosYaw / 2.0f);
        odom.pose.pose.orientation.w = Mathf.Cos(rosYaw / 2.0f);

        ros.Publish(topicName, odom);
    }
}
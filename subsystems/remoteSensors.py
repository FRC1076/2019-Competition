class AngleSensor:
    """
    Angle sensor has two main roles.   It listens on the specified
    port for udp angle packets and parses them to obtain the most
    recent value for the angle to target.  It also acts as a data
    source for a PIDController.

    If the target is to the left of the robot, the angle is reported
    as negative.

    Example:
        angleSensor = AngleSensor('10.10.76.7', 8812)

        This creates channel to listen on port 8812 for angle information.
    """
    def __init__(self, sensor_ip, listen_port):
        self.vision_ip = sensor_ip
        self.angle = 0

    def pidGet(self):
        # return cached value that was last received from
        # the vision system
        #
        return self.angle

class RangeSensor:
    """
    RangeSensor has two main functions.  The first is to listen on the specified listen_port
    for range packets from forward facing sonar units.  The second is to act as a datasource
    for PIDController object.

    Example:
        rangeSensor = RangeSensor('10.10.76.9', 8813)
    """
    def __init__(self, sensor_ip, listen_port):
        self.sonar_ip = sensor_ip
        self.range_cm = 0

    def pidGet(self):
        # return cached value that was last receive from
        # the sonar unit
        return self.range_cm


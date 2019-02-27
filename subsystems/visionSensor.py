import wpilib
import json
from lib1076.udp_channel import UDPChannel

class VisionSensor:
    """
    Vision sensor has two main roles.   It listens on the specified
    port for udp angle packets and parses them to obtain the most
    recent value for the angle to target.  It also acts as a data
    source for a PIDController.

    If the target is to the left of the robot, the angle is reported
    as negative.

    Example:
        visionSensor = VisionSensor('10.10.76.7', 8812)

        This creates channel to listen on port 8812 for angle information.
    """
    def __init__(self, sensor_ip, listen_port, simulation=False, logger=None):
        self.vision_ip = sensor_ip
        self.vision_port = listen_port
        self.logger = logger
        self.simulation = simulation
        if self.simulation is False:
            self.VISION_IP = self.vision_ip
            self.VISION_PORT = self.vision_port
            self.LOCAL_IP = "10.10.76.2"
        else:
            self.VISION_IP = "127.0.0.1"
            self.VISION_PORT = 8812
            self.LOCAL_IP = "127.0.0.1"
        self.bearing = 0
        self.range_cm = 0
        self.channel = self.createChannel()

    def pidGetBearing(self):
        # return cached bearing that was last received from
        # the vision system
        return self.bearing

    def pidGetRange(self):
        # return cached range that was last received from
        # the vision system
        return self.range_cm

    def getPIDSourceType(self):
        return wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement

    def createChannel(self):
        try:
            channel = UDPChannel(local_ip=self.LOCAL_IP, local_port=self.VISION_PORT, 
                                      remote_ip=self.VISION_IP, remote_port=self.VISION_PORT)
        except:
            channel = None
        return channel

    def receiveAngleUpdates(self):
        if self.channel is None:
            self.createChannel()
        else:
            (message, sender) = self.channel.receive_from()
            if message is not None:
                try:
                    message_dict = json.loads(message)
                    try:
                        self.range_cm = message_dict['range']
                        try:
                            self.bearing = message_dict['angle']
                        except message_dict['angle'] is None:
                            self.bearing = message_dict['bearing']
                        return self.range_cm, self.bearing
                    except KeyError:
                        if self.logger is not None:
                            self.logger.error("No bearing and/or range in message %s", message)
                except json.decoder.JSONDecodeError:
                    message_dict = None
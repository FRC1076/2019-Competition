import wpilib
import json
try:
    from frc1076lib.udp_channel import UDPChannel
except:
    from lib1076.udp_channel import UDPChannel

class SonarSensor:
    """
    SonarSensor has two main functions.  The first is to listen on the specified listen_port
    for range packets from forward facing sonar units.  The second is to act as a datasource
    for PIDController object.

    Example:
        sonarSensor = SonarSensor('10.10.76.9', 8813)
    """
    def __init__(self, sensor_ip, listen_port, logger=None):
        self.sonar_ip = sensor_ip
        self.sonar_port = listen_port
        self.logger = logger
        self.range_cm = 0

    def pidGet(self):
        # return cached value that was last receive from
        # the sonar unit
        return self.range_cm

    def getPIDSourceType(self):
        "Tell PID that sonar provides range not speed"
        return wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement

    def createChannel(self):
        sonar_ip = self.sonar_ip
        sonar_port = self.sonar_port
        try:
            self.channel = UDPChannel(local_ip="10.10.76.2", local_port=5811, 
                                      remote_ip=sonar_ip, remote_port=sonar_port)
        except:
            pass

    def recieveRangeUpdates(self):
        if self.channel is None:
            self.createChannel()
        else:
            (message, sender) = self.channel.receive_from()
            if message is not None:
                try:
                    message_dict = json.loads(message)
                    try:
                        self.range_cm = message_dict['range']
                        return self.range_cm
                    except KeyError:
                        if self.logger is not None:
                            self.logger.error("No range in message %s", message)
                except json.decoder.JSONDecodeError:
                    message_dict = None
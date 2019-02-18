import wpilib
import json
from lib1076.udp_channel import UDPChannel

class SonarSensor:
    """
    SonarSensor has two main functions.  The first is to listen on the specified listen_port
    for range packets from forward facing sonar units.  The second is to act as a datasource
    for PIDController object.

    Example:
        sonarSensor = SonarSensor('10.10.76.11', 5811)
    """
    def __init__(self, sensor_ip, listen_port, logger=None):
        self.sonar_ip = sensor_ip
        self.sonar_port = listen_port
        self.logger = logger
        self.range_cm = 0
        self.channel = self.createChannel()

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
            channel = UDPChannel(local_ip="10.10.76.2", local_port=sonar_port, 
                                 remote_ip=sonar_ip, remote_port=sonar_port)
        except:
            channel = None
        return channel

    def receiveRangeUpdates(self):
        if self.channel is None:
            if self.logger is not None:
                self.logger.info("Retrying to create the channel")
                print("Retry to create channel...")
            self.channel = self.createChannel()
        else:
            (message, sender) = self.channel.receive_from()
            if message is not None:
                self.logger.info("Received :",message)
                try:
                    message_dict = json.loads(message)
                    try:
                        self.range_cm = message_dict['range-cm']
                    except KeyError:
                        if self.logger is not None:
                            self.logger.error("No range-cm in message %s", message)
                            print("No range-cm in message")
                except json.decoder.JSONDecodeError:
                    # leave the self.range_cm value alone
                    if self.logger is not None:
                        self.logger.error("json parsing error, message: ",message)
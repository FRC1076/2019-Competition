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
    def __init__(self, sensor_ip, listen_port, simulation=False, logger=None):
        self.sonar_ip = sensor_ip
        self.sonar_port = listen_port
        self.logger = logger
        self.simulation = simulation
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
        if self.simulation is False:
            SONAR_IP = self.sonar_ip
            SONAR_PORT = self.sonar_port
            LOCAL_IP = "10.10.76.2"
        else:
            SONAR_IP = "127.0.0.1"
            SONAR_PORT = 8813
            LOCAL_IP = "127.0.0.1"
        
        try:
            channel = UDPChannel(local_ip=LOCAL_IP, local_port=SONAR_PORT, 
                                 remote_ip=SONAR_IP, remote_port=SONAR_PORT)
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
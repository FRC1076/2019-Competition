import wpilib
import json
from lib1076.udp_channel import UDPChannel
from statistics import mean

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
        self.wsize = 5
        self.range_window = []
        if self.simulation is False:
            self.SONAR_IP = self.sonar_ip
            self.SONAR_PORT = self.sonar_port
            self.LOCAL_IP = "10.10.76.2"
        else:
            self.SONAR_IP = "127.0.0.1"
            self.SONAR_PORT = 8813
            self.LOCAL_IP = "127.0.0.1"
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
        try:
            channel = UDPChannel(local_ip=self.LOCAL_IP, local_port=self.SONAR_PORT, 
                                 remote_ip=self.SONAR_IP, remote_port=self.SONAR_PORT)
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
                self.logger.info("Received %s from %s", message, sender)
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

    def filterWindow(self, new_value):
        wsize = self.wsize
        range_window = self.range_window

        # drop in the new value, trim to wsize elements
        self.range_window.insert(0, new_value)
        self.range_window = range_window[:wsize]

        # just return the reading if we do not have a full window
        if len(self.range_window) < wsize:
            return new_value
        else:
            # sort and then return the average w/o the hi and lo
            sorted_window = sorted(self.range_window)
            return mean(sorted_window[1:wsize-1])
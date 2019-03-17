import math
import time
from enum import Enum
import wpilib

# VisionAuto PID constants
VISION_P = 0.04
VISION_I = 0.00
VISION_D = 0.00

def vision_reckon(drivetrain, gyro, vision_socket):
    yield from Timed(VisionAuto(drivetrain, gyro, vision_socket, forward=1, look_for="retroreflective"), duration=30).run()

class BaseAutonomous:
    def init(self):
        return self

    def execute(self):
        pass

    def end(self):
        pass

    def run(self):
        def _execute():
            yield from self.execute()
            self.end()
        self.init()
        return _execute()

class VisionAuto(BaseAutonomous):
    """
    Rotate the robot towards the target using incoming vision packets
    vision_socket is a VisionSocket, not a Python socket
    """
    def __init__(self, drivetrain, gyro, vision_socket, forward, look_for):
        """
        forward is from 0 to 1
        look_for is "retroreflective"
        """
        self.drivetrain = drivetrain
        self.socket = vision_socket
        self.gyro = gyro
        self.forward = forward
        self.correction = 0
        self.look_for = look_for
        # PID Constants, tuned as of March 5th
        self.PID = wpilib.PIDController(VISION_P, VISION_I, VISION_D,
            source=self._get_angle,
            output=self._set_correction)

        print("P: ", VISION_P)
        print("I: ", VISION_I)
        print("D: ", VISION_D)

    def _get_angle(self):
        angle = self.socket.get_angle(key=self.look_for, max_staleness=0.5)
        if angle is None:
            return 0
        return angle

    def _set_correction(self, value):
        self.correction = value

    def init(self):
        self.PID.setInputRange(-35, 35)
        self.PID.enable()

    def execute(self):
        # Values to make angle correction smaller:
        # ~57% = (x / 1.75)
        # ~47% = (x / 2.13)
        # ~42% = (x / 2.38)
        # ~30% = (x / 3.33)
        while True:
            angle = self.socket.get_angle(key=self.look_for, max_staleness=0.5)
            if angle is not None:
                correction = self.correction
                # print("self.Correction: ", self.correction)
                # print("Correction: ", correction)
                correction = math.copysign(self.correction, angle)
                self.drivetrain.arcade_drive(self.forward, correction)
            else:
                self.drivetrain.arcade_drive(self.forward, 0)
            yield

    def end(self):
        self.PID.disable()

class RotateAutonomous(BaseAutonomous):
    """
    Rotate the robot by the specified angle in degrees.
    Positive values will rotate clockwise, while negative values will rotate
    counterclockwise.
    """
    def __init__(self, drivetrain, gyro, angle=0, turn_speed=0):
        self.drivetrain = drivetrain
        self.gyro = gyro
        self.speed = turn_speed
        assert self.speed >= 0, "Speed ({}) must be positive!".format(self.speed)
        self.angle_goal = angle

    def init(self):
        self.start_angle = self.gyro.getYaw()

    def execute(self):
        while True:
            # We need the different between the goal angle delta and the current angle delta
            angle_error = abs(self.angle_goal) - abs(self.start_angle - self.gyro.getYaw())

            if angle_error < 1.0:
                print("BROKE EARLY")
                break

            correction_factor = angle_error / 10.0
            if correction_factor > 1.0:
                correction_factor = 1.0
            if self.angle_goal > 0:
                self.drivetrain.arcade_drive(0, self.speed * correction_factor)
            else:
                self.drivetrain.arcade_drive(0, -self.speed * correction_factor)
            if angle_error > 1:
                yield

    def end(self):
        self.drivetrain.stop()
        
class Timed(BaseAutonomous):
    def __init__(self, auto, duration):
        self.auto = auto
        self.duration = duration

    def init(self):
        self.auto.init()
        self.end_time = time.time() + self.duration

    def execute(self):
        for _ in self.auto.execute():
            if time.time() > self.end_time:
                print("TIMED OUT!")
                break
            yield

    def end(self):
        self.auto.end()


class Timed(BaseAutonomous):
    def __init__(self, auto, duration):
        self.auto = auto
        self.duration = duration

    def init(self):
        self.auto.init()
        self.end_time = time.time() + self.duration

    def execute(self):
        for _ in self.auto.execute():
            if time.time() > self.end_time:
                print("TIMED OUT!")
                break
            yield

    def end(self):
        self.auto.end()





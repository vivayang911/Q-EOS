from core.config import (
    PID_KP,
    PID_KI,
    PID_KD
)


class PIDController:

    def __init__(
        self,
        kp=PID_KP,
        ki=PID_KI,
        kd=PID_KD
    ):

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.integral = 0
        self.previous_error = 0

    def calculate(
        self,
        target,
        current
    ):

        error = target - current

        self.integral += error

        derivative = (
            error -
            self.previous_error
        )

        output = (
            self.kp * error
            + self.ki * self.integral
            + self.kd * derivative
        )

        self.previous_error = error

        return round(
            output,
            2
        )
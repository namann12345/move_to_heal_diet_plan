import math
import numpy as np

def calculate_angle(a, b, c):
    """
    Calculates the angle between three 2D points: a, b, c.
    Point b is the vertex.
    Returns angle in degrees (0 - 180).
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/math.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

class SquatState:
    def __init__(self):
        self.stage = "up"
        self.counter = 0
        self.form_errors = []

    def update(self, hip_angle, knee_angle):
        self.form_errors = []
        
        # Check form
        if knee_angle < 90 and hip_angle < 60:
            self.form_errors.append("Perfect Depth")
        elif knee_angle < 90 and hip_angle > 90:
             self.form_errors.append("Keep your back straight and push hips back.")

        # State transition
        if knee_angle > 160:
            if self.stage == "down":
                self.stage = "up"
                self.counter += 1
                return True # rep completed
        elif knee_angle < 100:
            self.stage = "down"
            
        return False

# You can add PushUpState, LungeState etc. following the same pattern

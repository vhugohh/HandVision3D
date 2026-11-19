import numpy as np
from backend.hand_kinematics import quat

def test_identity_quaternion_is_normalized():
    q=quat(np.eye(3))
    assert abs(sum(v*v for v in q)-1)<1e-6

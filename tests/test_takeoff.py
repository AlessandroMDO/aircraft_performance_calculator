import unittest
import math

from functions.takeoff import climb_angle
class TestDistance(unittest.TestCase):

    def test_climb_angle(self):

        a = climb_angle(T=1000, D=600, W=800)
        self.assertAlmostEqual(a, math.pi/6, places=1)

        b = climb_angle(T=1500, D=600, W=800)
        self.assertAlmostEqual(b, 3, places=1)



if __name__ == '__main__':
    unittest.main()

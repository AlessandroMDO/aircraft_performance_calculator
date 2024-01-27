import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import unittest
from functions.gliding import gliding_range_endurance
import math
class TestDistance(unittest.TestCase):


    def test_range_endurance_cl_constant(self):

        aircraft_parameters = {
            "S": 10.5,
            "CL_MAX": 0.4,
            "CD0": 0.015,
            "K": 0.01857,
            "OEW": 0
        }

        flight_parameters   = {
            "NUMBER_OF_PASSENGERS": 0,
            "FUEL_WEIGHT": 0,
            "PAYLOAD_WEIGHT": 0,
            "landing_parameters": {'ALTITUDE_LANDING': 0},
            "CRUISE_ALTITUDE": 4000
        }

        results = gliding_range_endurance(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters, V_cru=25, W=525, graph=True)

        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_CONSTANT_LIFT_STANDARD']) == math.floor(89031.34)
        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_ENDURANCE_CONSTANT_LIFT_STANDARD']) == math.floor(5607.33)

        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_MAX_RANGE_CONSTANT_LIFT']) == math.floor(119833.55)
        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_ENDURANCE_MAX_RANGE_CONSTANT_LIFT_MAX']) == math.floor(11313)

        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_MAX_ENDURANCE_CONSTANT_LIFT']) == math.floor(103778.9)
        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_MAX_ENDURANCE_CONSTANT_LIFT']) == math.floor(12894.14)



        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_RANGE_CONSTANT_AIRSPEED']) == math.floor(43493.67)
        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_ENDURANCE_CONSTANT_AIRSPEED']) == math.floor(1739.75)


        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_MAX_RANGE_CONSTANT_AIRSPEED']) == math.floor(151504.56)
        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_ENDURANCE_MAX_RANGE_CONSTANT_AIRSPEED']) == math.floor(13131.38)









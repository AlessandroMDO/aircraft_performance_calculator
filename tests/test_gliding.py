import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import unittest
from functions.gliding import gliding_range_endurance, gliding_angle_rate_of_descent
import math
class TestGliding(unittest.TestCase):


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
            "DISPATCHED_CARGO_WEIGHT": 0,
            "landing_parameters": {'ALTITUDE_LANDING': 0},
            "CRUISE_ALTITUDE": 4000,
            "CRUISE_VELOCITY": 25
        }

        results = gliding_range_endurance(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters,
                                          W=525, graph_V=False, graph_CL=False, display=False)

        # CL
        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_CONSTANT_LIFT_STANDARD']) == math.floor(89031.34)
        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_ENDURANCE_CONSTANT_LIFT_STANDARD']) == math.floor(5607.33)

        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_MAX_RANGE_CONSTANT_LIFT']) == math.floor(119833.55)
        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_ENDURANCE_MAX_RANGE_CONSTANT_LIFT_MAX']) == math.floor(11313)

        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_MAX_ENDURANCE_CONSTANT_LIFT']) == math.floor(103778.9)
        assert math.floor(results['GLIDING_CONSTANT_LIFT']['GLIDING_MAX_ENDURANCE_CONSTANT_LIFT']) == math.floor(12894.14)


        # V
        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_RANGE_CONSTANT_AIRSPEED_STANDARD']) == math.floor(43493.67)
        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_ENDURANCE_CONSTANT_AIRSPEED_STANDARD']) == math.floor(1739.75)

        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_MAX_RANGE_CONSTANT_AIRSPEED']) == math.floor(151504.56)
        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_ENDURANCE_MAX_RANGE_CONSTANT_AIRSPEED']) == math.floor(13131.38)

        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_RANGE_MAX_ENDURANCE_CONSTANT_AIRSPEED']) == math.floor(145823.99)
        assert math.floor(results['GLIDING_CONSTANT_AIRSPEED']['GLIDING_MAX_ENDURANCE_CONSTANT_AIRSPEED']) == math.floor(13602.62)


    def test_gliding_angle_rate_of_descent(self):

        aircraft_parameters_1 = {
            "S": 15,
            "CD0": 0.015,
            "K": 0.03,
            "OEW": 0
        }

        flight_parameters_1   = {
            "NUMBER_OF_PASSENGERS": 0,
            "FUEL_WEIGHT": 0,
            "PAYLOAD_WEIGHT": 0,
            "DISPATCHED_CARGO_WEIGHT": 0,
            "CRUISE_VELOCITY": 30
        }

        results_1 = gliding_angle_rate_of_descent(aircraft_parameters=aircraft_parameters_1,
                                                  flight_parameters=flight_parameters_1, W=390, altitude=2000,
                                                  plot=False)

        assert math.floor(results_1['GLIDING_ANGLE']) == math.floor(-15.07)
        assert math.floor(results_1['GLIDING_RATE_OF_DESCENT']) == math.floor(7.89)


if __name__ == '__main__':
    unittest.main()







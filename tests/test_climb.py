import math
import unittest
from app.functions.climb import calc_max_climb_angle_rate_of_climb, calc_distance_time_steepest_climb

class TestGliding(unittest.TestCase):

    def test_climb_angle_rate_of_climb(self):

        aircraft_parameters = {
            "S": 525,
            "CD0": 0.017,
            "CL_MAX": 1.2,
            "K": 0.042,
            "T0": 0.27 * 1000,
            "TSFC": 1,
            "OEW": 1000,
            "NE": 1
        }

        flight_parameters = {
            "NUMBER_OF_PASSENGERS": 0,
            "FUEL_WEIGHT": 0,
            "PAYLOAD_WEIGHT": 0,
            "DISPATCHED_CARGO_WEIGHT": 0,
            "CRUISE_ALTITUDE": 40000 / 3.281,
            "CRUISE_VELOCITY": 100
        }

        response = calc_max_climb_angle_rate_of_climb(aircraft_parameters=aircraft_parameters,
                                                      flight_parameters=flight_parameters, plot=False, display=False)

        assert math.floor(math.degrees(response['MAX_GAMMA_CLIMB'])) == math.floor(5.17)
        print(round(response['MAX_RATE_OF_CLIMB'], 3))
        assert round(response['MAX_RATE_OF_CLIMB'], 3) == 0.286

    # def test_distance_time_steepest_climb(self):
    #
    #     aircraft_parameters = {
    #         "S": 525,
    #         "CD0": 0.017,
    #         "CL_MAX": 1.2,
    #         "K": 0.042,
    #         "T0": 0.27 * 15000,
    #         "TSFC": 1,
    #         "OEW": 15000,
    #         "NE": 1
    #     }
    #
    #     flight_parameters = {
    #         "NUMBER_OF_PASSENGERS": 0,
    #         "FUEL_WEIGHT": 0,
    #         "PAYLOAD_WEIGHT": 0,
    #         "DISPATCHED_CARGO_WEIGHT": 0,
    #         "CRUISE_ALTITUDE": 40000 / 3.281,
    #         "CRUISE_VELOCITY": 100
    #     }
    #
    #     response = calc_distance_time_steepest_climb(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)
    #     print(response)
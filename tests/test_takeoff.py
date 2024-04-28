import unittest
import math

from app.functions.takeoff import climb_angle, total_takeoff_distance, total_takeoff_time


class TestTakeoff(unittest.TestCase):

    def test_climb_angle(self):

        b = climb_angle(T=1500, D=600, W=800)
        self.assertAlmostEqual(b, math.radians(3), places=1)

    def test_total_takeoff_distance(self):
        aircraft_parameters = {
            "S": 9,
            "CD0": 0.016,
            "K": 0.052,
            "T0": 2600,
            "CL_MAX": 1.2,
            "TSFC": 0.8 / 3600,
            "OEW": 0,
            "NE": 1
        }

        flight_parameters = {

            "takeoff_parameters": {
                "WIND_VELOCITY_TAKEOFF": 1,
                "RUNWAY_SLOPE_TAKEOFF": 0,
                "ALTITUDE_TAKEOFF": 1400,
                "MU_TAKEOFF": 0.04
            },

            "landing_parameters": {
                "WIND_VELOCITY_LANDING": -3,
                "RUNWAY_SLOPE_LANDING": 1,
                "ALTITUDE_LANDING": 0,
                "MU_LANDING": 0.02
            },
            "NUMBER_OF_PASSENGERS": 0,
            "FUEL_WEIGHT": 3200,
            "PAYLOAD_WEIGHT": 0,
            "DISPATCHED_CARGO_WEIGHT": 0,
            "CRUISE_ALTITUDE": 9000,

        }

        result = total_takeoff_distance(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)
        print(result)

    def test_total_takeoff_time(self):

        aircraft_parameters = {
            "S": 9,
            "CD0": 0.016,
            "K": 0.052,
            "T0": 2600,
            "CL_MAX": 1.2,
            "TSFC": 0.8 / 3600,
            "OEW": 0,
            "NE": 1
        }

        flight_parameters = {

            "takeoff_parameters": {
                "WIND_VELOCITY_TAKEOFF": 1,
                "RUNWAY_SLOPE_TAKEOFF": 0,
                "ALTITUDE_TAKEOFF": 1400,
                "MU_TAKEOFF": 0.04
            },

            "landing_parameters": {
                "WIND_VELOCITY_LANDING": -3,
                "RUNWAY_SLOPE_LANDING": 1,
                "ALTITUDE_LANDING": 0,
                "MU_LANDING": 0.02
            },
            "NUMBER_OF_PASSENGERS": 0,
            "FUEL_WEIGHT": 3200,
            "PAYLOAD_WEIGHT": 0,
            "DISPATCHED_CARGO_WEIGHT": 0,
            "CRUISE_ALTITUDE": 9000,

        }

        result = total_takeoff_time(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)
        print(result)



if __name__ == '__main__':
    unittest.main()

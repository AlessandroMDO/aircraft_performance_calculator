import unittest

from app.functions.landing import calc_total_landing_time, calc_total_landing_distance

#TODO: ajustar cenários de teste
class TestLanding(unittest.TestCase):

    def test_total_landing_distance(self):
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

        result = calc_total_landing_distance(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)

    def test_total_landing_time(self):

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

        result = calc_total_landing_time(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)

if __name__ == '__main__':
    unittest.main()

import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import unittest
from functions.cruising_jet import get_cruise_velocity, cruising_jet_range, cruising_jet_endurance
import math
class TestGliding(unittest.TestCase):

    def test_get_cruise_velocity(self):

        aircraft_parameters = {
            "S": 475,
            "CD0": 0.017,
            "K": 0.042,
            "T0": 8e5,
            "CL_MAX": 0,
            "TSFC": 1,
            "OEW": 0,
            "NE": 1
        }

        flight_parameters = {
            "NUMBER_OF_PASSENGERS": 0,
            "FUEL_WEIGHT": 0,
            "PAYLOAD_WEIGHT": 0,
            "DISPATCHED_CARGO_WEIGHT": 0,
            "CRUISE_ALTITUDE": 38000 * 0.3048

        }

        W = 2.7e6
        V_STALL = 1000

        result = get_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters,
                                     W_CRUISE=W, V_STALL=V_STALL, T_CRUISE=8e5, plot=False)

        assert math.floor(result['CRUISE_VELOCITIES'][0]) in [math.floor(v) for v in [375.78, 143.30]]
        assert math.floor(result['CRUISE_VELOCITIES'][1]) in [math.floor(v) for v in [375.78, 143.30]]
        assert math.floor(result['MINIMUM_DRAG']) == math.floor(144292)

    def test_cruising_jet_range(self):

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
            "NUMBER_OF_PASSENGERS": 0,
            "FUEL_WEIGHT": 3200,
            "PAYLOAD_WEIGHT": 0,
            "DISPATCHED_CARGO_WEIGHT": 0,
            "CRUISE_ALTITUDE": 9000

        }

        V_CRU = 800 / 3.6
        zeta = 0.3

        result = cruising_jet_range(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters,
                                    V_CRUISE=V_CRU, W_CRUISE=36e3, zeta_CRUISE=zeta)

        assert math.floor(result['RANGE_CONSTANT_HEIGHT_CL']/1000) == math.floor(5075)
        assert math.floor(result['RANGE_CONSTANT_VELOCITY_CL']/1000) == math.floor(5541)
        assert math.floor(result['RANGE_CONSTANT_HEIGHT_VELOCITY']/1000) == math.floor(5040)

    def test_cruising_jet_endurance(self):

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
            "NUMBER_OF_PASSENGERS": 0,
            "FUEL_WEIGHT": 3200,
            "PAYLOAD_WEIGHT": 0,
            "DISPATCHED_CARGO_WEIGHT": 0,
            "CRUISE_ALTITUDE": 9000

        }

        V_CRU = 800 / 3.6
        zeta = 0.3

        result = cruising_jet_endurance(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters,
                                        V_CRUISE=V_CRU, W_CRUISE=36e3, zeta_CRUISE=zeta)

        assert math.floor(result['ENDURANCE_CONSTANT_HEIGHT_CL'] / 3600) == math.floor(6.93)
        assert math.floor(result['ENDURANCE_CONSTANT_VELOCITY_CL'] / 3600) == math.floor(6.93)
        assert math.floor(result['ENDURANCE_CONSTANT_HEIGHT_VELOCITY'] / 3600) == math.floor(6.3)








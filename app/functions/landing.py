"""
# -------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- LANDING ------------------------------------------------------ #
# -------------------------------------------------------------------------------------------------------------------- #



1. Approach distance and time
2. Flare distance and time
3. Rotation distance and time
4. Landing roll distance and time

x_la = x_ap + x_f + x_R_La + x_g_La
t_la = t_ap + t_f + t_R_La + t_g_La


gamma_Ap = approach slope, usualmente 3º (https://wiki.ivao.aero/en/home/training/documentation/IFR_Approach_procedure_-_Final_approach_segment#:~:text=In%20case%20of%20non-precision,runway%20centre%20line%20is%20mandatory.)
"""
import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from functions.aero import Aero
import math
from pandas import DataFrame
from numpy import linspace

aero = Aero()

# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------ LANDING ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def calc_total_landing_distance(aircraft_parameters: dict, flight_parameters: dict, altitude=None):

    gamma_Ap = aero.gamma_Ap
    V_wind = flight_parameters['landing_parameters']['WIND_VELOCITY_LANDING']

    S  = aircraft_parameters['S']
    altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING'] if altitude is None else altitude
    mu = flight_parameters['landing_parameters']['MU_LANDING']
    CL_max = aircraft_parameters['CL_MAX']
    rho = aero.get_density(altitude=altitude)

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)

    W_ap = TOW - 0.95 * FW

    V_S_Ap = math.sqrt((2 * W_ap / S) / (rho * CL_max))  # 16.22 OJHA

    V_Ap = 1.3 * V_S_Ap

    R_f = (V_Ap ** 2) / (0.08 * aero.g)
    h_f = R_f * (1 - math.cos(gamma_Ap))

    V_Td = 1.15 * V_S_Ap  # Página 382 - Secao 16.3.8

    d_breaking = aero.medium_breaking_constant + mu / 2

    x_ap = (aero.h_Sc - h_f) / math.tan(gamma_Ap)  # 16.21 OHJA
    x_f = ((V_Ap ** 2)/(0.08 * aero.g)) * math.sin(gamma_Ap)  # 16.25 OHJA
    x_R_La = 3 * V_Td  # 16.27 OHJA

    x_g_La = ((V_Td ** 2)/d_breaking) * (1 + V_wind/V_Td)

    x_la = x_ap + x_f + x_R_La + x_g_La

    landing_distance_result = {
        "LANDING_DISTANCE": x_la,
        "LANDING_APPROACH_DISTANCE": x_ap,
        "LANDING_ROTATION_DISTANCE": x_R_La,
        "LANDING_ROLL_DISTANCE": x_g_La,
        "LANDING_FLARE_DISTANCE": x_f}

    return landing_distance_result


def calc_total_landing_time(aircraft_parameters: dict, flight_parameters: dict, altitude=None):
    gamma_Ap = aero.gamma_Ap

    V_wind = flight_parameters['landing_parameters']['WIND_VELOCITY_LANDING']

    S = aircraft_parameters['S']
    altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING'] if altitude is None else altitude
    mu = flight_parameters['landing_parameters']['MU_LANDING']
    CL_max = aircraft_parameters['CL_MAX']
    rho = aero.get_density(altitude=altitude)

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)

    W_ap = TOW - 0.95 * FW

    V_S_Ap = math.sqrt((2 * W_ap / S) / (rho * CL_max))  # 16.22 OJHA

    V_Ap = 1.3 * V_S_Ap

    V_Td = 1.15 * V_S_Ap  # Página 382 - Secao 16.3.8

    d_breaking = aero.medium_breaking_constant + mu / 2

    R_f = (V_Ap ** 2) / (0.08 * aero.g)
    h_f = R_f * (1 - math.cos(gamma_Ap))

    x_ap = (aero.h_Sc - h_f) / math.tan(gamma_Ap)

    t_ap = x_ap / (V_Ap * math.cos(gamma_Ap))
    t_f = V_Ap * gamma_Ap / (0.08 * aero.g)  # 16.26 OJHA
    t_R_La = 3
    t_g_La = V_Td / d_breaking

    t_la = t_ap + t_f + t_R_La + t_g_La

    landing_time_result = {
        "LANDING_TIME": t_la,
        "LANDING_APPROACH_TIME": t_ap,
        "LANDING_ROTATION_TIME": t_R_La,
        "LANDING_ROLL_TIME": t_g_La,
        "LANDING_FLARE_TIME": t_f}

    return landing_time_result


def calc_landing_distance_time_per_altitude(flight_parameters, aircraft_parameters, altitude=None):

    landing_altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING'] if altitude is None else altitude

    altitude_range = [round(i, -1) for i in linspace(0.5 * landing_altitude, min(30 * landing_altitude, 3500), 10)]

    landing_distance_range = [
        round(calc_total_landing_distance(flight_parameters=flight_parameters, aircraft_parameters=aircraft_parameters,
                                          altitude=alti)['LANDING_DISTANCE'], 2)
        for alti in altitude_range]

    landing_time_range = [
        round(calc_total_landing_time(flight_parameters=flight_parameters, aircraft_parameters=aircraft_parameters,
                                      altitude=alti)['LANDING_TIME'], 2)
        for alti in altitude_range]

    df = DataFrame(index=altitude_range, data={
        'Landing Distance [m]': landing_distance_range, 'Landing Time [s]': landing_time_range})
    df.index.name = 'Altitude [m]'

    return df


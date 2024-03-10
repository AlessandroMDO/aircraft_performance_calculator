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

aero = Aero()


# -------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- APPROACH ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

# def approach_distance(V_S, flight_parameters=None, aircraft_parameters=None):
#     """
#
#     Args:
#         V_S: velocidade de stall
#
#     Returns:
#         x_Ap = distancia percorrida durante a fase de approach
#
#     """
#
#     S  = aircraft_parameters['S']
#     altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING']
#     CL_max = aircraft_parameters['CL_MAX']
#     rho = aero.get_density(altitude=altitude)
#
#     NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
#     FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
#     CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
#     OEW = aircraft_parameters['OEW']
#
#     TOW = float(NP * aero.person_weight + OEW + FW + CW)
#
#     gamma_Ap = aero.gamma_Ap  # 3 deg
#     W_ap = TOW - 0.95 * FW
#     V_S_Ap = math.sqrt((2 * W_ap / S) / (rho * CL_max))  # 16.22 OJHA
#     V_Ap = 1.3 * V_S_Ap
#
#     R_f = (V_Ap ** 2) / (0.08 * aero.g)
#     h_f = R_f * (1 - math.cos(gamma_Ap))
#
#     if h_f > aero.h_Sc:
#         x_Ap = 0
#     else:
#         x_Ap = (aero.h_Sc - h_f) / math.tan(gamma_Ap)
#
#     return x_Ap


# def approach_time(V_S, altitude, S, CL_max, W_Ap, aircraft_parameters, flight_parameters):
#
#     # W_Ap = peso da aeronave no pouso. Ou seja, bem menos do que o peso de decolagem, já que consumiu combustível
#     # S = áre alar
#     # C_Lm_Ap = maximum lift coefficient (CL_max)
#     # rho = densidade do local de pouso
#
#     W_Ap = W_Ap
#     C_Lm_Ap = CL_max
#
#     rho = aero.get_density(altitude=altitude)
#     gamma_Ap = aero.gamma_Ap
#     x_Ap = approach_distance(V_S, aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)
#     V_Ap = (2 * (W_Ap / S) / (rho * C_Lm_Ap)) ** 0.5
#     t_Ap = x_Ap / (V_Ap * math.cos(gamma_Ap))
#
#     return t_Ap


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------ FLARE ------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

# def flare_distance(V_S):
#
#     gamma_Ap = aero.gamma_Ap
#     V_Ap = 1.3 * V_S
#     x_f = ((V_Ap ** 2) / (0.08 * aero.g)) * math.sin(gamma_Ap)  # 16.25 OJHA
#     return x_f
#
#
# def flare_time(V_S):
#
#     gamma_Ap = aero.gamma_Ap
#     V_Ap = 1.3 * V_S
#     t_f = (V_Ap * gamma_Ap) / (0.08 * aero.g)  # 16.26 OJHA
#     return t_f


# -------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- ROTATION ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

# def rotation_distance(V_S):
#     V_Td = 1.15 * V_S
#     x_R_La = 3 * V_Td
#     return x_R_La
#
#
# def rotation_time():
#     t_R_La = 3  # [s]
#     return t_R_La


# -------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------- LANDING ROLL --------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

# def landing_roll_distance(V_S, V_wind):
#
#     V_Td = 1.15 * V_S
#     d = aero.medium_breaking_constant * aero.g
#
#     x_g_La = (V_Td + V_wind) * (V_Td / (2 * d))
#
#     return x_g_La
#
#
# def landing_roll_time(V_S, V_wind):
#
#     V_Td = 1.15 * V_S
#     d = aero.medium_breaking_constant * aero.g
#
#     t_g_La = (V_Td / d) * (1 + V_wind)
#
#     return t_g_La


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------ LANDING ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


# def total_landing_distance(aircraft_parameters: dict, flight_parameters: dict, show=False):
#
#     altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING']
#
#     CL_max = aircraft_parameters['CL_MAX']
#     S = aircraft_parameters['S']
#     rho = aero.get_density(altitude=altitude)
#
#     V_wind = flight_parameters['landing_parameters']['WIND_VELOCITY_LANDING']
#
#     NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
#     FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
#     CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
#     OEW = aircraft_parameters['OEW']
#
#     TOW = float(NP * aero.person_weight + OEW + FW + CW)
#
#     V_S = aero.calculate_stall_velocity(W=TOW, CL_max=CL_max, S=S, rho=rho)
#
#     x_ap = approach_distance(V_S, flight_parameters=flight_parameters, aircraft_parameters=aircraft_parameters)
#     x_f = flare_distance(V_S=V_S)
#     x_R_La = rotation_distance(V_S=V_S)
#     x_g_La = landing_roll_distance(V_S=V_S, V_wind=V_wind)
#
#     x_la = x_ap + x_f + x_R_La + x_g_La
#
#     landing_distance_result = {
#         "LANDING_DISTANCE": x_la,
#         "LANDING_APPROACH_DISTANCE": x_ap,
#         "LANDING_ROTATION_DISTANCE": x_R_La,
#         "LANDING_ROLL_DISTANCE": x_g_La,
#         "LANDING_FLARE_DISTANCE": x_f}
#
#     return landing_distance_result


# def total_landing_time(aircraft_parameters: dict, flight_parameters: dict, show=False):
#
#     altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING']
#     V_wind = flight_parameters['landing_parameters']['WIND_VELOCITY_LANDING']
#
#     CL_max = aircraft_parameters['CL_MAX']
#     S = aircraft_parameters['S']
#     rho = aero.get_density(altitude=altitude)
#
#     NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
#     FW = flight_parameters['FUEL_WEIGHT']           # fuel weight
#     CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
#     OEW = aircraft_parameters['OEW']
#
#     TOW = float(NP * aero.person_weight + OEW + FW + CW)
#
#     W_Ap = TOW - 0.95 * FW
#
#     V_S = aero.calculate_stall_velocity(W=TOW, CL_max=CL_max, S=S, rho=rho)
#
#     t_ap = approach_time(altitude=altitude, S=S, V_S=V_S, W_Ap=W_Ap, CL_max=CL_max,
#                          aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)
#     t_f = flare_time(V_S=V_S)
#     t_R_La = rotation_time()
#     t_g_La = landing_roll_time(V_S=V_S, V_wind=V_wind)
#
#     t_la = t_ap + t_f + t_R_La + t_g_La
#
#     landing_time_result = {
#         "LANDING_TIME": t_la,
#         "LANDING_APPROACH_TIME": t_ap,
#         "LANDING_ROTATION_TIME": t_R_La,
#         "LANDING_ROLL_TIME": t_g_La,
#         "LANDING_FLARE_TIME": t_f}
#
#     return landing_time_result




def calc_landing_distance(aircraft_parameters: dict, flight_parameters: dict):

    gamma_Ap = aero.gamma_Ap
    V_wind = flight_parameters['landing_parameters']['WIND_VELOCITY_LANDING']

    S  = aircraft_parameters['S']
    altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING']
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

def calc_landing_time(aircraft_parameters: dict, flight_parameters: dict):
    gamma_Ap = aero.gamma_Ap

    V_wind = flight_parameters['landing_parameters']['WIND_VELOCITY_LANDING']

    S = aircraft_parameters['S']
    altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING']
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


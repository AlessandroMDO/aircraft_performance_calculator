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
from functions.utils import *
import math

c = Aero()


# -------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- APPROACH ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def approach_distance(V_S):
    """

    Args:
        V_S: velocidade de stall

    Returns:
        x_Ap = distancia percorrida durante a fase de approach

    """
    gamma_Ap = c.gamma_Ap
    V_Ap = 1.3 * V_S
    R_f = (V_Ap ** 2) / (0.08 * c.g)
    h_f = R_f * (1 - math.cos(gamma_Ap))

    if h_f > c.h_Sc:
        x_Ap = 0
    else:
        x_Ap = (c.h_Sc - h_f) / math.tan(gamma_Ap)

    return x_Ap


def approach_time(V_S, altitude, S, aircraft_parameters):

    # W_Ap = peso da aeronave no pouso. Ou seja, bem menos do que o peso de decolagem, já que consumiu combustível
    # S = áre alar
    # C_Lm_Ap = maximum lift coefficient (CL_max)
    # rho = densidade do local de pouso

    W_Ap = aircraft_parameters['MTOW'] - 0.8 * aircraft_parameters['PAYLOAD_WEIGHT']
    C_Lm_Ap = aircraft_parameters['CL_MAX']

    rho = c.get_density(altitude=altitude)
    gamma_Ap = c.gamma_Ap
    x_Ap = approach_distance(V_S)
    V_Ap = (2 * (W_Ap / S) / (rho * C_Lm_Ap)) ** 0.5
    t_Ap = x_Ap / (V_Ap * math.cos(gamma_Ap))

    return t_Ap


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------ FLARE ------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def flare_distance(V_S):

    gamma_Ap = c.gamma_Ap
    V_Ap = 1.3 * V_S
    x_f = ((V_Ap ** 2) / (0.08 * c.g)) * math.sin(gamma_Ap)
    return x_f


def flare_time(V_S):

    gamma_Ap = c.gamma_Ap
    V_Ap = 1.3 * V_S
    t_f = (V_Ap * gamma_Ap) / (0.08 * c.g)
    return t_f


# -------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- ROTATION ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def rotation_distance(V_S):
    V_Td = 1.15 * V_S
    x_R_La = 3 * V_Td
    return x_R_La


def rotation_time():
    t_R_La = 3  # [s]
    return t_R_La


# -------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------- LANDING ROLL --------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def landing_roll_distance(V_S, V_wind=0):

    V_Td = 1.15 * V_S
    d = c.medium_breaking_constant * c.g

    x_g_La = (V_Td + V_wind) * (V_Td / (2 * d))

    return x_g_La


def landing_roll_time(V_S, V_wind=0):

    V_Td = 1.15 * V_S
    d = c.medium_breaking_constant * c.g

    t_g_La = (V_Td / d) * (1 + V_wind)

    return t_g_La


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------ LANDING ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def total_landing_distance(parameters_dict, show=False):

    V_S = parameters_dict['V_S']

    x_ap = approach_distance(V_S)
    x_f = flare_distance(V_S=V_S)
    x_R_La = rotation_distance(V_S=V_S)
    x_g_La = landing_roll_distance(V_S=V_S)

    x_la = x_ap + x_f + x_R_La + x_g_La

    landing_distance_result = {
        "landing_distance": x_la,
        "landing_approach_distance": x_ap,
        "landing_rotation_distance": x_R_La,
        "landing_roll_distance": x_g_La,
        "landing_flare_distance": x_f}

    if show:
        print_formatted_string(how="top")
        print_formatted_string(input_string=f'LANDING DISTANCE: {round(x_la, 2)} [m]', how="center")
        print_formatted_string()
        print_formatted_string(input_string=f'APPROACH DISTANCE: {round(x_ap, 2)} [m]', how="left")
        print_formatted_string(input_string=f'FLARE DISTANCE: {round(x_f, 2)} [m]', how="left")
        print_formatted_string(input_string=f'ROTATION DISTANCE: {round(x_R_La, 2)} [m]', how="left")
        print_formatted_string(input_string=f'LANDING ROLL DISTANCE: {round(x_g_La, 2)} [m]', how="left")
        print_formatted_string(how="bottom")

    return landing_distance_result


def total_landing_time(V_S, S, altitude, aircraft_parameters, show=False):

    # W_Ap = aircraft_parameters['MTOW'] - 0.8 * aircraft_parameters['PAYLOAD_WEIGHT']

    t_ap = approach_time(altitude=altitude, S=S, aircraft_parameters=aircraft_parameters, V_S=V_S)
    t_f = flare_time(V_S=V_S)
    t_R_La = rotation_time()
    t_g_La = landing_roll_time(V_S=V_S)

    t_la = t_ap + t_f + t_R_La + t_g_La

    landing_time_result = {
        "landing_time": t_la,
        "landing_approach_time": t_ap,
        "landing_rotation_time": t_R_La,
        "landing_roll_time": t_g_La,
        "landing_flare_time": t_f}

    if show:
        print_formatted_string(how="top")
        print_formatted_string(input_string=f'LANDING TIME: {round(t_la, 2)} [s]', how="center")
        print_formatted_string()
        print_formatted_string(input_string=f'APPROACH TIME: {round(t_ap, 2)} [s]', how="left")
        print_formatted_string(input_string=f'FLARE TIME: {round(t_f, 2)} [s]', how="left")
        print_formatted_string(input_string=f'ROTATION TIME: {round(t_R_La, 2)} [s]', how="left")
        print_formatted_string(input_string=f'LANDING ROLL TIME: {round(t_g_La, 2)} [s]', how="left")
        print_formatted_string(how="bottom")

    return landing_time_result


#landing_distance(V_S=80, show=True)

"""
# -------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- TAKEOFF ------------------------------------------------------ #
# -------------------------------------------------------------------------------------------------------------------- #


The performance analysis of takeoff consists of calculating the distance and time covered during the takeoff phase.

x_to = x_g + x_r + x_tr + x_cl
t_to = t_g + t_r + t_tr + t_cl

x_to ; t_to  = takeoff distance; takeoff time               [m]; [s]
x_g  ; t_g   = ground round distance; ground round time     [m]; [s]
x_r  ; t_r   = rotation distance; rotation time             [m]; [s]
x_tr ; t_tr  = transition distance; transition time         [m]; [s]
x_cl ; t_cl  = climb distance; climb time                   [m]; [s]

V_S     = stall speed                                       [m/s]
V_L0    = litoff speed, usually 1.15*V_S                    [m/s]
T       = thrust                                            [N]
L       = lift                                              [N]
D       = drag                                              [N]
W       = weight                                            [N]
mu      = coefficient of friction                           [-]

The aircraft weight [W] in the bellow equations is considered to be constant because only a insignifcant fraction of
the fuel is consumed during the ground run.
"""
import os
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from functions.aero import Aero
from functions.utils import *
import math
from functools import lru_cache

c = Aero()



def climb_angle(T, D, W):
    gamma = math.asin((T - D) / W)  # [rad]

    return gamma


# -------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------- GROUND RUN ---------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def ground_run_acceleration(W_takeoff, mu, V_S, altitude, S, K, CD0, CL_max):
    # L e D precisa ser calculado considerando a velocidade de decolagem em 0.7 * (V_L0 = 1.15 * V_S)
    # W é o peso de decolagem
    # Pagina 386
    V_L0 = 1.15 * V_S
    rho = c.get_density(altitude=altitude)
    # TODO: Abner usou CL_LO = 0.8 CL_MAX
    CL_L0 = 0.8 * CL_max
    V = 0.7 * V_L0
    q = (rho * V ** 2) / 2
    L = CL_L0 * q * S
    D = (CD0 + K * CL_L0 ** 2) * q * S
    T = 10 * D
    a = (c.g / W_takeoff) * (T - D - mu * (W_takeoff - L))  # [m/s^2]

    return a


def ground_run_distance(V_S, W, mu,  CD0, K, S, altitude, CL_max, V_wind=0, theta_runway=0):

    a = ground_run_acceleration(W_takeoff=W, mu=mu, V_S=V_S, CD0=CD0, K=K, S=S, altitude=altitude, CL_max=CL_max)
    V_L0 = 1.15 * V_S
    x_g = ((V_L0 + V_wind) ** 2) / (2 * (a + c.g * math.sin(theta_runway)))  # [m] Página 385

    return x_g


def ground_run_time(V_S, W, mu, CD0, K, S, altitude, CL_max, V_wind=0, theta_runway=0):

    a = ground_run_acceleration(W_takeoff=W, mu=mu, V_S=V_S, CD0=CD0, K=K, S=S, altitude=altitude, CL_max=CL_max)
    V_L0 = 1.15 * V_S
    t_g = (V_L0 + V_wind) / (a + c.g * math.sin(theta_runway))  # [s]

    return t_g


# -------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- ROTATION ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def rotation_time():
    t_r = 3  # [s]

    return t_r


def rotation_distance(V_S):
    t_r = rotation_time()
    V_L0 = 1.15 * V_S
    x_r = t_r * V_L0  # [m]

    return x_r


# -------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------- TRANSITION ---------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def transition_distance(V_S, T, D, W):
    V_L0 = 1.15 * V_S
    gamma = climb_angle(T=T, D=D, W=W)
    R_tr = (V_L0 ** 2) / (0.15 * c.g)
    x_tr = R_tr * math.sin(gamma)  # [m]

    return x_tr


def transition_time(V_S, T, W, D):
    V_L0 = 1.15 * V_S
    gamma = climb_angle(T=T, D=D, W=W)
    R_tr = (V_L0 ** 2) / (0.15 * c.g)
    t_tr = (R_tr * gamma) / V_L0  # [s]

    return t_tr


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------- CLIMB ------------------------------------------------------ #
# -------------------------------------------------------------------------------------------------------------------- #


def climb_distance(T, D, V_S, W):

    V_L0 = 1.15 * V_S
    gamma = climb_angle(T=T, D=D, W=W)
    R_tr = (V_L0 ** 2) / (0.15 * c.g)
    h_tr = (1 - math.cos(gamma)) * R_tr

    if c.h_Sc - h_tr:
        x_cl = 0
    else:
        x_cl = (c.h_Sc - h_tr) / math.tan(gamma)  # [m]

    return x_cl


def climb_time(T, D, V_S, W):
    gamma = climb_angle(T=T, D=D, W=W)
    x_cl = climb_distance(T=T, D=D, V_S=V_S, W=W)
    V_cl = 1.3 * V_S  # página 382
    t_cl = x_cl / (V_cl * math.cos(gamma))

    return t_cl  # [s]


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------ TAKEOFF ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def total_takeoff_distance(takeoff_parameters, aircraft_parameters, show=False):

    V_wind = takeoff_parameters['WIND_VELOCITY_TAKEOFF']
    theta_runway = takeoff_parameters['RUNWAY_SLOPE_TAKEOFF']
    altitude = takeoff_parameters['ALTITUDE_TAKEOFF']
    mu = takeoff_parameters['MU_TAKEOFF']
    V_S = takeoff_parameters['STALL_VELOCITY']

    # Como calcular estes valors ?!
    T = takeoff_parameters['T']
    D = takeoff_parameters['D']

    W = aircraft_parameters['MTOW']
    S = aircraft_parameters['SURFACE_AREA']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']


    x_g = ground_run_distance(V_S=V_S, W=W, mu=mu, V_wind=V_wind, theta_runway=theta_runway, altitude=altitude, S=S, K=K, CD0=CD0, CL_max=0.8)
    x_r = rotation_distance(V_S=V_S)
    x_cl = climb_distance(T=T, D=D, V_S=V_S, W=W)
    x_tr = transition_distance(V_S=V_S, T=T, D=D, W=W)

    x_to = x_g + x_r + x_tr + x_cl  # [m]

    takeoff_distance_result = {
        "takeoff_distance": x_to,
        "takeoff_ground_distance": x_g,
        "takeoff_rotation_distance": x_r,
        "takeoff_transition_distance": x_tr,
        "takeoff_climb_distance": x_cl}

    if show:
        print_formatted_string(how="top")
        print_formatted_string(input_string=f'TAKEOFF DISTANCE: {round(x_to, 2)} [m]', how="center")
        print_formatted_string()
        print_formatted_string(input_string=f'GROUND DISTANCE: {round(x_g, 2)} [m]', how="left")
        print_formatted_string(input_string=f'ROTATION DISTANCE: {round(x_r, 2)} [m]', how="left")
        print_formatted_string(input_string=f'CLIMB DISTANCE: {round(x_cl, 2)} [m]', how="left")
        print_formatted_string(input_string=f'TRANSITION DISTANCE: {round(x_tr, 2)} [m]', how="left")
        print_formatted_string(how="bottom")

    return takeoff_distance_result


def total_takeoff_time(takeoff_parameters, aircraft_parameters, show=False):

    V_wind = takeoff_parameters['WIND_VELOCITY_TAKEOFF']
    theta_runway = takeoff_parameters['RUNWAY_SLOPE_TAKEOFF']
    altitude = takeoff_parameters['ALTITUDE_TAKEOFF']
    mu = takeoff_parameters['MU_TAKEOFF']
    V_S = takeoff_parameters['STALL_VELOCITY']

    T = takeoff_parameters['T']
    D = takeoff_parameters['D']

    W = aircraft_parameters['MTOW']
    S = aircraft_parameters['SURFACE_AREA']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']
    CL_max = aircraft_parameters['CL_MAX']

    t_g = ground_run_time(V_S=V_S, W=W, mu=mu, V_wind=V_wind, theta_runway=theta_runway, CD0=CD0, K=K, S=S, altitude=altitude, CL_max=CL_max)
    t_r = rotation_time()
    t_tr = transition_time(V_S=V_S, T=T, W=W, D=D)
    t_cl = climb_time(T=T, D=D, V_S=V_S, W=W)

    t_to = t_g + t_r + t_tr + t_cl  # [s]

    takeoff_time_result = {
        "takeoff_time": t_to,
        "takeoff_ground_time": t_g,
        "takeoff_rotation_time": t_r,
        "takeoff_transition_time": t_tr,
        "takeoff_climb_time": t_cl}

    if show:
        print_formatted_string(how="top")
        print_formatted_string(input_string=f'TAKEOFF TIME: {round(t_to, 2)} [s]', how="center")
        print_formatted_string()
        print_formatted_string(input_string=f'GROUND TIME: {round(t_g, 2)} [s]', how="left")
        print_formatted_string(input_string=f'ROTATION TIME: {round(t_r, 2)} [s]', how="left")
        print_formatted_string(input_string=f'CLIMB TIME: {round(t_cl, 2)} [s]', how="left")
        print_formatted_string(input_string=f'TRANSITION TIME: {round(t_tr, 2)} [s]', how="left")
        print_formatted_string(how="bottom")

    return takeoff_time_result


# Estratégias de otimização para a distância de decolagem estão na página 389.
# total_takeoff_distance(T=200, D=100, L=1000, W=700, mu=0.3, V_S=30, V_wind=30, theta_runway=0,show=True, altitude=1000, S = 40, K=0.3)
# total_takeoff_time(T=200, D=100, L=1000, W=700, mu=0.3, V_S=30, V_wind=30,theta_runway=0,show=False)

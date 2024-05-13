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
from .utils import get_logger
from numpy import linspace
from pandas import DataFrame
import math

aero = Aero()
logger = get_logger()


def climb_angle(T, D, W):
    """
    Calcula o ângulo de subida durante a decolagem.

    Parâmetros:
    - T (float): Empuxo disponível durante a decolagem.
    - D (float): Arrasto durante a decolagem.
    - W (float): Peso da aeronave.

    Retorna:
    float: Ângulo de subida em radianos.
    """

    try:
        num = T - D
        gamma = math.asin(num / W)  # [rad]

        if gamma >= math.radians(3.5):
            gamma = math.radians(3.5)
        elif gamma <= math.radians(1):
            gamma = math.radians(1.5)

    except ValueError:
        gamma = math.radians(3)
    return gamma


# -------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------- GROUND RUN ---------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def ground_run_acceleration(W_takeoff, mu, V_S, altitude, S, K, CD0, CL_max, T0, thrust_factor):
    # L e D precisa ser calculado considerando a velocidade de decolagem em 0.7 * (V_L0 = 1.15 * V_S)
    # W é o peso de decolagem
    # Pagina 386

    V_L0 = 1.15 * V_S
    rho = aero.get_density(altitude=altitude)

    CL_L0 = 0.8 * CL_max

    V = 0.7 * V_L0

    q = (rho * V ** 2) / 2
    L = CL_L0 * q * S
    D = 0.5 * rho * (V ** 2) * S * CD0 + 2 * K * S * ((W_takeoff / S) ** 2) * 1 / (rho * V ** 2)

    T = aero.calculate_general_thrust(altitude=altitude, sea_level_thrust=T0, thrust_factor=thrust_factor)

    a = (aero.g / W_takeoff) * (T - D - mu * (W_takeoff - L))  # [m/s^2]

    if a < 0:
        a = 1

    return a


def ground_run_distance(V_S, W, mu, CD0, K, S, altitude, CL_max, T0, thrust_factor, V_wind=0, theta_runway=0):
    a = ground_run_acceleration(W_takeoff=W, mu=mu, V_S=V_S, CD0=CD0, K=K, S=S, altitude=altitude, CL_max=CL_max, T0=T0,
                                thrust_factor=thrust_factor)
    V_L0 = 1.15 * V_S
    x_g = ((V_L0 + V_wind) ** 2) / (2 * (a + aero.g * math.sin(theta_runway)))  # [m] Página 385

    return x_g


def ground_run_time(V_S, W, mu, CD0, K, S, altitude, CL_max, T0, thrust_factor, V_wind=0, theta_runway=0):
    a = ground_run_acceleration(W_takeoff=W, mu=mu, V_S=V_S, CD0=CD0, K=K, S=S, altitude=altitude, CL_max=CL_max, T0=T0,
                                thrust_factor=thrust_factor)

    V_L0 = 1.15 * V_S
    t_g = (V_L0 + V_wind) / (a + aero.g * math.sin(theta_runway))  # [s]

    return t_g

# -------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------- TRANSITION ---------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def transition_time(V_S, T, W, D):
    V_L0 = 1.15 * V_S
    gamma = climb_angle(T=T, D=D, W=W)
    R_tr = (V_L0 ** 2) / (0.15 * aero.g)
    t_tr = (R_tr * gamma) / V_L0  # [s]

    return t_tr


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------- CLIMB ------------------------------------------------------ #
# -------------------------------------------------------------------------------------------------------------------- #


def climb_distance(T, D, V_S, W):
    """
    Calcula a distância de subida durante a decolagem.

    Parâmetros:
    - T (float): Empuxo disponível durante a decolagem.
    - D (float): Arrasto durante a decolagem.
    - V_S (float): Velocidade de estol da aeronave.
    - W (float): Peso da aeronave.

    Retorna:
    float: Distância de subida necessária durante a decolagem.
    """

    V_L0 = 1.15 * V_S
    gamma = climb_angle(T=T, D=D, W=W)
    R_tr = (V_L0 ** 2) / (0.15 * aero.g)
    h_tr = (1 - math.cos(gamma)) * R_tr

    if aero.h_Sc - h_tr < 0:
        x_cl = 0
    else:
        x_cl = (aero.h_Sc - h_tr) / math.tan(gamma)  # [m]

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
def calc_total_takeoff_distance(flight_parameters, aircraft_parameters, altitude=None, show=False):

    V_wind = flight_parameters['takeoff_parameters']['WIND_VELOCITY_TAKEOFF']
    theta_runway = math.radians(flight_parameters['takeoff_parameters']['RUNWAY_SLOPE_TAKEOFF'])
    altitude = flight_parameters['takeoff_parameters']['ALTITUDE_TAKEOFF'] if altitude is None else altitude
    mu = flight_parameters['takeoff_parameters']['MU_TAKEOFF']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']
    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    CL_max = aircraft_parameters['CL_MAX']
    thrust_factor = (aircraft_parameters['TSFC'] / 3600)

    rho = aero.get_density(altitude=altitude)
    V_S = aero.calculate_stall_velocity(W=TOW, CL_max=CL_max, S=S, rho=rho)

    V_L0 = 1.15 * V_S
    V = 0.7 * V_L0
    D = 0.5 * rho * (V ** 2) * S * CD0 + 2 * K * S * ((TOW / S) ** 2) * 1 / (rho * V ** 2)

    x_g = ground_run_distance(V_S=V_S, W=TOW, mu=mu, V_wind=V_wind, theta_runway=theta_runway, altitude=altitude, S=S,
                              K=K, CD0=CD0, CL_max=CL_max, T0=T, thrust_factor=thrust_factor)

    x_r = (t_r := 3) * V_L0

    x_cl = climb_distance(T=T, D=D, V_S=V_S, W=TOW)

    gamma = climb_angle(T=T, D=D, W=TOW)
    R_tr = (V_L0 ** 2) / (0.15 * aero.g)
    x_tr = R_tr * math.sin(gamma)  # [m]

    x_to = x_g + x_r + x_tr + x_cl  # [m]

    takeoff_distance_result = {
        "TAKEOFF_DISTANCE": x_to,
        "TAKEOFF_GROUND_DISTANCE": x_g,
        "TAKEOFF_ROTATION_DISTANCE": x_r,
        "TAKEOFF_TRANSITION_DISTANCE": x_tr,
        "TAKEOFF_CLIMB_DISTANCE": x_cl}

    return takeoff_distance_result


def calc_total_takeoff_time(flight_parameters, aircraft_parameters, altitude=None, show=False):

    V_wind = flight_parameters['takeoff_parameters']['WIND_VELOCITY_TAKEOFF']
    theta_runway = math.radians(flight_parameters['takeoff_parameters']['RUNWAY_SLOPE_TAKEOFF'])
    altitude = flight_parameters['takeoff_parameters']['ALTITUDE_TAKEOFF'] if altitude is None else altitude
    mu = flight_parameters['takeoff_parameters']['MU_TAKEOFF']

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']
    CL_max = aircraft_parameters['CL_MAX']
    T0 = aircraft_parameters['T0']
    thrust_factor = (aircraft_parameters['TSFC'] / 3600)
    T = T0 * aircraft_parameters['NE']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)
    W = TOW

    rho = aero.get_density(altitude=altitude)
    V_S = aero.calculate_stall_velocity(W=W, CL_max=CL_max, S=S, rho=rho)

    V_L0 = 1.15 * V_S
    V = 0.7 * V_L0
    D = 0.5 * rho * (V ** 2) * S * CD0 + 2 * K * S * ((TOW / S) ** 2) * 1 / (rho * V ** 2)

    t_g = ground_run_time(V_S=V_S, W=W, mu=mu, V_wind=V_wind, theta_runway=theta_runway, CD0=CD0, K=K, S=S,
                          altitude=altitude, CL_max=CL_max, T0=T, thrust_factor=thrust_factor)
    t_r = 3
    t_tr = transition_time(V_S=V_S, T=T, W=W, D=D)
    t_cl = climb_time(T=T, D=D, V_S=V_S, W=W)

    t_to = t_g + t_r + t_tr + t_cl  # [s]

    takeoff_time_result = {
        "TAKEOFF_TIME": t_to,
        "TAKEOFF_GROUND_TIME": t_g,
        "TAKEOFF_ROTATION_TIME": t_r,
        "TAKEOFF_TRANSITION_TIME": t_tr,
        "TAKEOFF_CLIMB_TIME": t_cl}

    return takeoff_time_result


# Estratégias de otimização para a distância de decolagem estão na página 389.

def calc_takeoff_distance_time_per_altitude(flight_parameters, aircraft_parameters, altitude=None):
    takeoff_altitude = flight_parameters['takeoff_parameters']['ALTITUDE_TAKEOFF'] if altitude is None else altitude

    altitude_range = [round(i, -1) for i in linspace(0.5 * takeoff_altitude, min(30 * takeoff_altitude, 3500), 10)]

    takeoff_distance_range = [
        round(calc_total_takeoff_distance(flight_parameters=flight_parameters, aircraft_parameters=aircraft_parameters,
                                          altitude=alti)['TAKEOFF_DISTANCE'], 2)
        for alti in altitude_range]

    takeoff_time_range = [
        round(calc_total_takeoff_time(flight_parameters=flight_parameters, aircraft_parameters=aircraft_parameters,
                                      altitude=alti)['TAKEOFF_TIME'], 2)
        for alti in altitude_range]

    df = DataFrame(index=altitude_range, data={
        'Takeoff Distance [m]': takeoff_distance_range, 'Takeoff Time [s]': takeoff_time_range})
    df.index.name = 'Altitude [m]'
    return df
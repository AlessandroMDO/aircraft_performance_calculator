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

    """
    Calcula a distância total de pouso de uma aeronave com base nos parâmetros de voo e parâmetros físicos da aeronave.

    Parâmetros:
    - aircraft_parameters (dict): Dicionário contendo os parâmetros da aeronave.
        - 'S' (float): Área da asa (m²).
        - 'CL_MAX' (float): Coeficiente de sustentação máximo (adimensional).
        - 'OEW' (float): Peso operacional vazio da aeronave (N).
    - flight_parameters (dict): Dicionário contendo os parâmetros de voo e de pouso.
        - 'NUMBER_OF_PASSENGERS' (int): Número de passageiros.
        - 'FUEL_WEIGHT' (float): Peso de combustível (N).
        - 'DISPATCHED_CARGO_WEIGHT' (float): Peso de carga despachada (N).
        - 'landing_parameters' (dict): Dicionário contendo parâmetros específicos de pouso.
            - 'WIND_VELOCITY_LANDING' (float): Velocidade do vento durante o pouso (m/s).
            - 'ALTITUDE_LANDING' (float): Altitude do pouso (m).
            - 'MU_LANDING' (float): Coeficiente de atrito para o pouso.
    - altitude (float, opcional): Altitude do pouso (m). Se não fornecido, usa o valor de 'ALTITUDE_LANDING'.

    Retorna:
    - dict: Dicionário contendo as seguintes informações:
        - 'LANDING_DISTANCE' (float): Distância total de pouso calculada (m).
        - 'LANDING_APPROACH_DISTANCE' (float): Distância de aproximação durante o pouso (m).
        - 'LANDING_ROTATION_DISTANCE' (float): Distância de rotação durante o pouso (m).
        - 'LANDING_ROLL_DISTANCE' (float): Distância de rolagem durante o pouso (m).
        - 'LANDING_FLARE_DISTANCE' (float): Distância de flare durante o pouso (m).
    """

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

    """
    Calcula o tempo total de pouso de uma aeronave com base nos parâmetros de voo e parâmetros físicos da aeronave.

    Parâmetros:
    - aircraft_parameters (dict): Dicionário contendo os parâmetros da aeronave.
        - 'S' (float): Área da asa (m²).
        - 'CL_MAX' (float): Coeficiente de sustentação máximo (adimensional).
        - 'OEW' (float): Peso operacional vazio da aeronave (N).
    - flight_parameters (dict): Dicionário contendo os parâmetros de voo e de pouso.
        - 'NUMBER_OF_PASSENGERS' (int): Número de passageiros.
        - 'FUEL_WEIGHT' (float): Peso de combustível (N).
        - 'DISPATCHED_CARGO_WEIGHT' (float): Peso de carga despachada (N).
        - 'landing_parameters' (dict): Dicionário contendo parâmetros específicos de pouso.
            - 'WIND_VELOCITY_LANDING' (float): Velocidade do vento durante o pouso (m/s).
            - 'ALTITUDE_LANDING' (float): Altitude do pouso (m).
            - 'MU_LANDING' (float): Coeficiente de atrito para o pouso.
    - altitude (float, opcional): Altitude do pouso (m). Se não fornecido, usa o valor de 'ALTITUDE_LANDING'.

    Retorna:
    - dict: Dicionário contendo as seguintes informações:
        - 'LANDING_TIME' (float): Tempo total de pouso calculado (s).
        - 'LANDING_APPROACH_TIME' (float): Tempo de aproximação durante o pouso (s).
        - 'LANDING_ROTATION_TIME' (float): Tempo de rotação durante o pouso (s).
        - 'LANDING_ROLL_TIME' (float): Tempo de rolagem durante o pouso (s).
        - 'LANDING_FLARE_TIME' (float): Tempo de flare durante o pouso (s).
    """

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

    """
    Calcula a distância de pouso e o tempo de pouso para diferentes altitudes de pouso, variando de metade da altitude
    de pouso até no máximo 3500 m.

    Parâmetros:
    - flight_parameters (dict): Dicionário contendo os parâmetros de voo e de pouso.
        - 'landing_parameters' (dict): Dicionário contendo parâmetros específicos de pouso.
            - 'ALTITUDE_LANDING' (float): Altitude de pouso (m).
    - aircraft_parameters (dict): Dicionário contendo os parâmetros da aeronave.
    - altitude (float, opcional): Altitude específica de pouso (m). Se não fornecido, usa o valor de 'ALTITUDE_LANDING'.

    Retorna:
    - pandas.DataFrame: DataFrame contendo as seguintes colunas:
        - 'Landing Distance [m]': Distância de pouso calculada para cada altitude de pouso (m).
        - 'Landing Time [s]': Tempo de pouso calculado para cada altitude de pouso (s).
    """

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


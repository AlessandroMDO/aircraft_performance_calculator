import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------ RANGE ------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


# Página 325 OKJA
import sys

sys.path.append('functions')
from .utils import hash_dict, print_formatted_string, get_logger, linspace
import matplotlib.pyplot as plt
# from aero import Aero
import math
# import numpy as np
from functools import lru_cache
from .aero import Aero

aero = Aero()


def calc_cruise_velocity(aircraft_parameters: dict, flight_parameters: dict, W_CRUISE=None, V_STALL=None,
                         T_CRUISE=None, plot=False, display=False):
    altitude = flight_parameters['CRUISE_ALTITUDE']
    sigma = aero.get_sigma(altitude=altitude)

    rho_0 = aero.rho_0
    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    S = aircraft_parameters['S']
    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']
    n = (aircraft_parameters['TSFC'] / 3600)
    CL_max = aircraft_parameters['CL_MAX']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)

    # TOW - (50% do combustível)
    W = TOW - 0.5 * FW if W_CRUISE is None else W_CRUISE

    T_CRU = aero.calculate_general_thrust(altitude=altitude, sea_level_thrust=T,
                                          thrust_factor=n) if T_CRUISE is None else T_CRUISE

    E_m = aircraft_parameters['E_m']

    V_11 = (T_CRU * sigma ** n) / (sigma * rho_0 * S * CD0)
    V_12 = 1 - (1 / (E_m ** 2)) * ((W ** 2) / ((T_CRU * sigma ** n) ** 2))

    V_1 = V_11 * (1 + math.sqrt(V_12))
    V_2 = V_11 * (1 - math.sqrt(V_12))

    V_cru_1 = math.sqrt(max(V_1, 0))
    V_cru_2 = math.sqrt(max(V_2, 0))

    V_S = aero.calculate_stall_velocity(W=W, CL_max=CL_max, S=S, rho=rho_0) if V_STALL is None else V_STALL

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        # Selecionamos a maior velocidade de cruzeiro
        V_cru = max(V_cru_1, V_cru_2) if (V_cru_1 > V_S and V_cru_2 > V_S) else V_cru_1 if (
                    V_cru_1 > V_S > V_cru_2) else V_cru_2
    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    D_min = (2 * W) * (K * CD0) ** 0.5

    if plot is True:

        lista_arrasto_total = []
        lista_arrasto_parasita = []
        lista_arrasto_induzido = []

        v_range = linspace(max(0.1 * V_cru, 50), min(V_cru + 300, 600), 50)

        for v in v_range:
            arrasto_parasita = 0.5 * sigma * rho_0 * (v ** 2) * S * CD0
            arrasto_induzido = (2 * K * W ** 2) / (sigma * rho_0 * S * v ** 2)

            arrasto_total = arrasto_parasita + arrasto_induzido

            lista_arrasto_total.append(arrasto_total)
            lista_arrasto_parasita.append(arrasto_parasita)
            lista_arrasto_induzido.append(arrasto_induzido)

        fig_cruzeiro = plt.figure(figsize=(5, 3))
        plt.plot(v_range, [i / 1e3 for i in lista_arrasto_total], c='black', label="Total Drag")
        plt.plot(v_range, [i / 1e3 for i in lista_arrasto_parasita], c='black', ls='--', label="Parasitic Drag")
        plt.plot(v_range, [i / 1e3 for i in lista_arrasto_induzido], c='black', ls='-.', label="Induced Drag")
        plt.plot(v_range, [T_CRU / 1e3] * len(v_range), label="Thrust", ls=(0, (5, 10)), color='black')
        plt.scatter(v_range[lista_arrasto_total.index(min(lista_arrasto_total))], min(lista_arrasto_total) / 1e3,
                    c='black', label=f"Minimum Drag = {round(D_min / 1e3, 2)}")
        plt.xlabel("Velocity [m/s]", size=12)
        plt.ylabel("Drag [kN]", size=12)
        plt.title("Thrust and drag per velocity")
        plt.grid()
        plt.legend()

        if display is True:
            plt.show()
        else:
            pass

    result = {
        "CRUISE_VELOCITY": V_cru,
        "MINIMUM_DRAG": D_min,
        "CRUISE_VELOCITIES": [V_cru_1, V_cru_2],
        "CRUISE_DRAG_GRAPH": fig_cruzeiro if plot is True else None
    }

    return result


def calc_cruising_jet_range(aircraft_parameters: dict, flight_parameters: dict, V_CRUISE=None, W_CRUISE=None,
                            zeta_CRUISE=None, plot=False, display=False):
    # 9.3.1 - Maximum Range of constant altitude-constant lift coefficient flight (página 239)
    # 9.3.2 - Maximum Range of constant airspeed-constant lift coefficient flight (página 241)
    # 9.3.3 - Maximum Range of constant altitude-airspeed (página 243)

    logger = get_logger(log_name="Cruise")

    """
    Calcula o alcance de cruzeiro de uma aeronave a jato com base nos parâmetros da aeronave, altitude e peso.

    Parâmetros:
    - aircraft_parameters: Um dicionário contendo os parâmetros da aeronave, incluindo 'TSFC', 'WING_AREA', 'K', 'TOW', 'OPERATIONAL_WEIGHT', 'MAX_PAYLOAD_WEIGHT', 'CD0', e 'CL_MAX'.
    - altitude: Altitude em metros.
    - W: Peso da aeronave em Newtons.
    - show: Um sinalizador booleano que indica se os resultados devem ser exibidos (opcional, padrão é False).

    Retorna:
    Um dicionário contendo três casos de faixa de voo:
    - "range_constant_height_cl": Faixa para voo com altura constante e coeficiente de sustentação constante.
    - "range_constant_velocity_cl": Faixa para voo com velocidade constante e coeficiente de sustentação constante.
    - "range_constant_height_velocity": Faixa para voo com altitude constante e velocidade constante.

    Se show for True, também exibe os resultados formatados.

    Notas:
    - A função assume que a função calc_cruise_velocity() está definida e disponível no escopo.
    """

    c = (aircraft_parameters['TSFC'] / 3600)

    altitude = flight_parameters['CRUISE_ALTITUDE']
    logger.debug(f"calc_cruising_jet_range| Altitude: {altitude}")

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        V_cru = calc_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)[
            'CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE
    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    logger.debug(f"calc_cruising_jet_range| V_cru: {V_cru}")

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    sigma = aero.get_sigma(altitude=altitude)
    logger.debug(f"calc_cruising_jet_range | Sigma: {sigma}")

    TOW = float(NP * aero.person_weight + OEW + FW + CW) if W_CRUISE is None else W_CRUISE
    logger.debug(f"TOW: {TOW}")

    W_1 = TOW - 0.15 * FW
    logger.info(f"W_1: {W_1}")
    W_2 = TOW - 0.95 * FW

    zeta = ((W_1 - W_2) / W_1) if zeta_CRUISE is None else zeta_CRUISE
    logger.info(f"Zeta: {zeta}")

    CD0 = aircraft_parameters['CD0']

    CL_cru = (2 * W_1) / (S * aero.rho_0 * sigma * V_cru ** 2)
    logger.debug(f"calc_cruising_jet_range| CL_cru: {CL_cru}")

    CD_cru = CD0 + K * CL_cru ** 2
    logger.debug(f"CD_cru: {CD_cru}")

    E_cru = CL_cru / CD_cru
    logger.debug(f"E_cru: {E_cru}")

    E_m = aircraft_parameters['E_m']

    # -----------------------------------------------------------------------------------------------------------------#
    # CASE 1 - Range and Flight Parameters of Constant Altitude-Constant Lift Coefficient Flight

    # OJHA 8.16
    x_h_CL = (2 * E_cru * V_cru / c) * (1 - math.sqrt(1 - zeta))  # OK
    E_m_h_CL = 1 / (2 * math.sqrt(K * CD0))

    # OJHA 9.16
    x_mr_h_CL = math.sqrt(3 * math.sqrt(3) * 0.5) * math.sqrt((2 * W_1 / S) / (aero.rho_0 * sigma)) * (
                math.sqrt(E_m_h_CL / CD0) / c) * (1 - math.sqrt(1 - zeta))
    # -----------------------------------------------------------------------------------------------------------------#
    # Case 2 - Range and Flight Parameters of Constant Airspeed-Constant Lift Coefficient Flight
    # OJHA - 8.23
    x_V_CL = ((E_cru * V_cru) / c) * math.log(1 / (1 - zeta))

    t_loiter = 1.16 * (x_V_CL / V_cru)  # Approximate Method of Deriving Loiter Time from Range (Eq 9)

    E_m_V_CL = 1 / (2 * math.sqrt(K * CD0))  # Equação 9.15 [OK]
    V1_Em = math.sqrt((2 * W_1 / S) / (aero.rho_0 * sigma)) * (K / CD0) ** 0.25  # Equação 9.15 [OK]

    # E_mr_V_CL = math.sqrt(3) * E_m_V_CL / 2  # Equação 9.23 [OK]
    # V_mr_V_CL = (3 ** 0.25) * V1_Em  # Equação 9.21 [OK]

    # x_mr_V_CL = (E_mr_V_CL * V_mr_V_CL / c) * math.log(1 / (1 - zeta))  # Equação 9.24 [OK]

    # Equação 9.26 [OK]
    x_mr_V_CL = (1 / (2 * c)) * math.sqrt(3 * math.sqrt(3) / 2) * math.sqrt(
        (2 * W_1 / S) / (aero.rho_0 * sigma)) * math.sqrt(E_m / CD0) * math.log(1 / (1 - zeta))

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight
    # OJHA - 8.35
    x_h_V = ((2 * V_cru * E_m) / c) * math.atan(E_cru * zeta / (2 * E_m * (1 - K * E_cru * CL_cru * zeta)))

    zeta_rix = zeta

    # OJHA - Equação 9.47
    x_mr_h_V = (
            ((1 / c) * math.sqrt(2 * E_m / CD0)) *
            math.sqrt((2 * W_1 / S) / (aero.rho_0 * sigma)) *
            ((3 * (1 - zeta_rix)) ** 0.25) *
            math.atan((zeta * math.sqrt(3 * (1 - zeta_rix))) / ((1 - zeta) + 3 * (1 - zeta_rix))))

    ranges = {
        "RANGE_CONSTANT_HEIGHT_CL": round(x_h_CL, 2),
        "MAX_RANGE_CONSTANT_HEIGHT_CL": round(x_mr_h_CL, 2),
        "LOITER_TIME": round(t_loiter, 2),

        "RANGE_CONSTANT_VELOCITY_CL": round(x_V_CL, 2),
        "MAX_RANGE_CONSTANT_VELOCITY_CL": round(x_mr_V_CL, 2),

        "RANGE_CONSTANT_HEIGHT_VELOCITY": round(x_h_V, 2),
        "MAX_RANGE_CONSTANT_HEIGHT_VELOCITY": round(x_mr_h_V, 2)
    }

    return ranges


# -------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------- ENDURANCE ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def calc_cruising_jet_endurance(aircraft_parameters: dict, flight_parameters: dict,
                                W_CRUISE=None, V_CRUISE=None, zeta_CRUISE=None, show=False):
    logger = get_logger(log_name="Cruise")

    c = (aircraft_parameters['TSFC'] / 3600)

    altitude = flight_parameters['CRUISE_ALTITUDE']

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        V_cru = calc_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)[
            'CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE

    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    logger.debug(f"V_cru: {V_cru}")

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    sigma = aero.get_sigma(altitude=altitude)
    logger.debug(f"Sigma: {sigma}")

    TOW = float(NP * aero.person_weight + OEW + FW + CW) if W_CRUISE is None else W_CRUISE
    logger.debug(f"TOW: {TOW}")

    W_1 = TOW - 0.15 * FW
    logger.info(f"W_1: {W_1}")
    W_2 = TOW - 0.95 * FW

    zeta = ((W_1 - W_2) / W_1) if zeta_CRUISE is None else zeta_CRUISE
    logger.debug(f"calc_cruising_jet_endurance | zeta: {sigma}")

    CD0 = aircraft_parameters['CD0']
    CL_cru = (2 * W_1) / (S * aero.rho_0 * sigma * V_cru ** 2)

    CD_cru = CD0 + K * (CL_cru ** 2)
    E_cru = CL_cru / CD_cru

    E_m = aircraft_parameters['E_m']

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 1 - Range and Flight Parameters of Constant Altitude-Constant Lift Coefficient Flight
    t_h_CL = (E_cru / c) * math.log(1 / (1 - zeta))

    E_t_m_h_CL = E_m
    t_m_h_CL = (E_t_m_h_CL / c) * math.log(1 / (1 - zeta))  # Equação 9.79 [OK]

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 2 - Range and Flight Parameters of Constant Airspeed-Constant Lift Coefficient Flight
    t_V_CL = (E_cru / c) * math.log(1 / (1 - zeta))

    E_t_m_V_CL = E_m
    t_m_V_CL = (E_t_m_V_CL / c) * math.log(1 / (1 - zeta))  # Equação 9.79 [OK]

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight
    t_h_V = (2 * E_m / c) * math.atan((E_cru * zeta) / (2 * E_m * (1 - K * E_cru * CL_cru * zeta)))

    zeta_rix = zeta
    E_t_m_h_V = E_m

    # Equação 9.85 [OK]
    t_m_h_V = (
            (2 * E_t_m_h_V / c) *
            math.atan(
                (zeta * math.sqrt(1 - zeta_rix)) / ((1 - zeta) + (1 - zeta_rix)))
    )

    endurance = {
        "ENDURANCE_CONSTANT_HEIGHT_CL": t_h_CL,
        "MAX_ENDURANCE_CONSTANT_HEIGHT_CL": t_m_h_CL,

        "ENDURANCE_CONSTANT_VELOCITY_CL": t_V_CL,
        "MAX_ENDURANCE_CONSTANT_VELOCITY_CL": t_m_V_CL,

        "ENDURANCE_CONSTANT_HEIGHT_VELOCITY": t_h_V,
        "MAX_ENDURANCE_CONSTANT_HEIGHT_VELOCITY": t_m_h_V
    }

    return endurance


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------- PAYLOAD x RANGE -------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

def calc_payload_x_range(aircraft_parameters: dict, flight_parameters: dict, V_CRUISE=None, display=False):
    logger = get_logger(log_name="Cruise")

    n = (aircraft_parameters['TSFC'] / 3600)
    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']

    altitude = flight_parameters['CRUISE_ALTITUDE']  # Cruise Height
    h_cru = altitude

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        V_cru = calc_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)[
            'CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE

    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    MFW = aircraft_parameters['MAXIMUM_FUEL_WEIGHT']  # max fuel weight

    # NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    # CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']
    MTOW = aircraft_parameters['MTOW']
    MPW = aircraft_parameters['MAXIMUM_PAYLOAD_WEIGHT']
    logger.debug(f"calc_payload_x_range | MTOW : {MTOW}")

    E_m = aircraft_parameters['E_m']

    def range_iter(W, zeta):

        range_list = []

        V_i = V_cru

        # for V_i in linspace(V_cru - 50, V_cru + 50, 20):

        rho_i = aero.get_density(altitude=h_cru)
        CL_i = (2 * W) / (S * rho_i * V_i ** 2)
        CD_i = CD0 + K * CL_i ** 2
        E_i = CL_i / CD_i

        # -----------------------------------------------------------------------------------------------------------------#
        # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight

        x_h_V = (2 * V_i * E_i / n) * math.atan((E_i * zeta) / (2 * E_m * (1 - K * E_i * CL_i * zeta)))

        range_list.append(x_h_V)

        return max(range_list)

    y_A = MPW / aero.g  # condição de máxima carga paga, porém sem combustível (alcance zero)
    x_A = 0

    y_B = MPW / aero.g  # MTOW
    zeta_B = (MTOW - OEW - MPW) / MTOW

    y_C = max((MTOW - OEW - MFW) / aero.g, 0)  # Aumenta o combustível, porém reduz carga paga
    zeta_C = MFW / MTOW

    y_D = 0  # Zero carga paga
    zeta_D = MFW / (MFW + OEW)



    x_B = range_iter(zeta=zeta_B, W=MTOW)
    x_C = range_iter(zeta=zeta_C, W=MTOW)
    x_D = range_iter(zeta=zeta_D, W=OEW + MFW)

    # Ponto A:
    xy_A = [x_A / 1000, y_A / 1000]
    # Ponto B:
    xy_B = [x_B / 1000, y_B / 1000]
    # Ponto C:
    xy_C = [x_C / 1000, y_C / 1000]
    # Ponto D:
    xy_D = [x_D / 1000, y_D / 1000]

    fig_payload_range = plt.figure(figsize=(5, 3))

    plt.plot([xy_A[0], xy_B[0]], [xy_A[1], xy_B[1]], linewidth=2.5, c="#1D3D7B")
    plt.plot([xy_B[0], xy_C[0]], [xy_B[1], xy_C[1]], linewidth=2.5, c="#1D3D7B")
    plt.plot([xy_C[0], xy_D[0]], [xy_C[1], xy_D[1]], linewidth=2.5, c="#1D3D7B")

    plt.scatter(xy_A[0], xy_A[1], c="#1D3D7B")
    plt.scatter(xy_B[0], xy_B[1], c="#1D3D7B")
    plt.scatter(xy_C[0], xy_C[1], c="#1D3D7B")
    plt.scatter(xy_D[0], xy_D[1], c="#1D3D7B")

    plt.annotate(text="A", xy=(xy_A[0], xy_A[1]))
    plt.annotate(text="B", xy=(xy_B[0], xy_B[1]))
    plt.annotate(text="C", xy=(xy_C[0], xy_C[1]))
    plt.annotate(text="D", xy=(xy_D[0], xy_D[1]))

    plt.ylabel("Payload [kN]", fontsize=12)
    plt.title("Diagram Payload vs. Range", fontsize=14)
    plt.xlabel("Range [km]", fontsize=12)
    plt.legend()
    plt.grid(True)

    if display is True:
        plt.show()
    else:
        pass

    return fig_payload_range


def calc_cruise_fuel_weight(aircraft_parameters: dict, flight_parameters: dict, W_CRUISE=None, V_CRUISE=None):
    logger = get_logger(log_name="Cruise")

    c = (aircraft_parameters['TSFC'] / 3600)

    altitude = flight_parameters['CRUISE_ALTITUDE']

    if flight_parameters['CRUISE_VELOCITY'] == 0:

        # Se for zero, quremos computar o valor
        V_cru = calc_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)[
            'CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE

    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW) if W_CRUISE is None else W_CRUISE
    logger.debug(f"TOW: {TOW}")

    W_1 = TOW - 0.15 * FW

    sigma = aero.get_sigma(altitude=altitude)
    S = aircraft_parameters['S']
    K = aircraft_parameters['K']

    E_m = aircraft_parameters['E_m']
    CD0 = aircraft_parameters['CD0']

    CL_cru = (2 * W_1) / (S * aero.rho_0 * sigma * V_cru ** 2)

    CD_cru = CD0 + K * (CL_cru ** 2)
    E_cru = CL_cru / CD_cru

    departure_coods = {
        "LATITUDE": flight_parameters['takeoff_parameters']['LATITUDE_TAKEOFF'],
        "LONGITUDE": flight_parameters['takeoff_parameters']['LONGITUDE_TAKEOFF']
    }

    arrival_cords = {
        "LATITUDE": flight_parameters['landing_parameters']['LATITUDE_LANDING'],
        "LONGITUDE": flight_parameters['landing_parameters']['LONGITUDE_LANDING']
    }

    covered_distance_cruise = aero.get_haversine_distance(departure=departure_coods, arrival=arrival_cords)
    logger.debug(f"covered_distance_cruise | covered_distance_cruise : {covered_distance_cruise / 1000}")

    # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight
    # OJHA - 8.35
    # x_h_V = ((2 * V_cru * E_m) / c) * math.atan(E_cru * zeta / (2 * E_m * (1 - K * E_cru * CL_cru * zeta)))
    x_h_V = covered_distance_cruise

    # zeta = 2*E_m*math.tan(c*x_h_V/(2*E_m*V_cru))/(E_cru*(2*CL_cru*E_m*K*math.tan(c*x_h_V/(2*E_m*V_cru)) + 1))
    zeta = (2 * E_m *
            math.tan(c * x_h_V / (2 * E_m * V_cru)) /
            (E_cru * (2 * CL_cru * E_m * K * math.tan(c * x_h_V / (2 * E_m * V_cru)) + 1))
            )

    logger.debug(f"calc_cruise_fuel_weight | zeta : {zeta}")
    W_2 = W_1 * (1 - zeta)

    delta_fuel = W_1 - W_2
    percent_reduction = delta_fuel / W_1
    logger.debug(f"calc_cruise_fuel_weight | percent_reduction : {percent_reduction * 100}")
    logger.debug(f"calc_cruise_fuel_weight | needed fuel weight [ton] : {(delta_fuel / 9.81) / 1000}")

    logger.debug(f"calc_cruise_fuel_weight | W_1 : {W_1}")
    logger.debug(f"calc_cruise_fuel_weight | W_2 : {W_2}")
    logger.debug(f"calc_cruise_fuel_weight | F_W : {FW}")

    valid_fuel = delta_fuel > FW

    if valid_fuel is True:
        logger.debug(f"Quantidade insuficiente. calc_cruise_fuel_weight | W2: {W_2}\n delta:{delta_fuel}")
    else:
        logger.debug(f"Quantidade suficiente. calc_cruise_fuel_weight | W2: {W_2}\n delta:{delta_fuel}")

    return {
        "DELTA_FUEL": delta_fuel,
        "ZETA": zeta,
        "VALID_FUEL": valid_fuel
    }

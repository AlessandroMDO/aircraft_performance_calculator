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
# sys.path.append(os.path.abspath("..functions/aero.py"))
# os.system("python aero.py")
from .utils import hash_dict, print_formatted_string, get_logger, linspace
import matplotlib.pyplot as plt
# from aero import Aero
import math
# import numpy as np
from functools import lru_cache
from .aero import Aero


aero = Aero()

def get_cruise_velocity(aircraft_parameters: dict, flight_parameters: dict, W_CRUISE=None, V_STALL=None, T_CRUISE=None, plot=False, display=False):

    """
        Calcula a velocidade de cruzeiro de uma aeronave com base nos parâmetros da aeronave, altitude e peso.

        Parâmetros:
        - aircraft_parameters: Um dicionário contendo os parâmetros da aeronave, incluindo 'ZERO_THRUST', 'SURFACE_AREA', 'CD0', 'K', 'THRUST_FACTOR', e 'CL_MAX'.
        - altitude: Altitude em metros.
        - W: Peso da aeronave em Newtons. # TODO qual peso usar aqui?
        - plot: Um sinalizador booleano que indica se deve ser gerado um gráfico de empuxo e arrasto (opcional, padrão é False).

        Retorna:
        - V_cru: Velocidade de cruzeiro em metros por segundo.
        - fig_cruzeiro: (Opcional) Figura do gráfico de empuxo e arrasto, gerada apenas se plot for True.
        """

    altitude = flight_parameters['CRUISE_ALTITUDE']
    sigma = aero.get_sigma(altitude=altitude)

    rho_0  = aero.rho_0
    T0     = aircraft_parameters['T0']
    S      = aircraft_parameters['S']
    CD0    = aircraft_parameters['CD0']
    K      = aircraft_parameters['K']
    n      = aircraft_parameters['TSFC']
    CL_max = aircraft_parameters['CL_MAX']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    MTOW = float(NP * aero.person_weight + OEW + FW + CW)
    # MTOW - (50% do combustível)
    W = MTOW - 0.5 * FW if W_CRUISE is None else W_CRUISE

    T = T0 * aircraft_parameters['NE']

    T_CRU = aero.calculate_general_thrust(altitude=altitude, sea_level_thrust=T, thrust_factor=n) if T_CRUISE is None else T_CRUISE

    E_m = 1 / (2 * math.sqrt(K * CD0))

    V_11 = (T_CRU * sigma ** n)/(sigma * rho_0 * S * CD0)
    V_12 = 1 - (1/(E_m ** 2))*((W ** 2) / ((T_CRU * sigma ** n) ** 2))

    V_1 = V_11 * (1 + math.sqrt(V_12))
    V_2 = V_11 * (1 - math.sqrt(V_12))

    V_cru_1 = math.sqrt(max(V_1, 0))
    V_cru_2 = math.sqrt(max(V_2, 0))

    V_S = aero.calculate_stall_velocity(W=W, CL_max=CL_max, S=S, rho=rho_0) if V_STALL is None else V_STALL

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        # Selecionamos a maior velocidade de cruzeiro
        V_cru = max(V_cru_1, V_cru_2) if (V_cru_1 > V_S and V_cru_2 > V_S) else V_cru_1 if (V_cru_1 > V_S > V_cru_2) else V_cru_2
    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']



    D_min = (2 * W) * (K * CD0) ** 0.5

    if plot is True:

        lista_arrasto_total    = []
        lista_arrasto_parasita = []
        lista_arrasto_induzido = []

        v_range = linspace(max(V_cru - 500, 100), V_cru + 300, 50)

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
        plt.plot(v_range, [T_CRU / 1e3] * len(v_range), label="Empuxo", ls=(0, (5, 10)), color='black')
        plt.scatter(v_range[lista_arrasto_total.index(min(lista_arrasto_total))], min(lista_arrasto_total) / 1e3, c='black', label=f"Minimum Drag = {round(D_min / 1e3, 2)}")
        plt.xlabel("Velocity [m/s]", size=12)
        plt.ylabel("Drag [kN]", size=12)
        plt.title("Relação empuxo e arrasto por velocidade")
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
        "CRUISE_DRAG_GRAPH": fig_cruzeiro if display is True else None
    }

    return result


def cruising_jet_range(aircraft_parameters: dict, flight_parameters: dict, V_CRUISE=None, W_CRUISE=None, zeta_CRUISE=None, plot=False, display=False):

    # 9.3.1 - Maximum Range of constant altitude-constant lift coefficient flight (página 239)
    # 9.3.2 - Maximum Range of constant airspeed-constant lift coefficient flight (página 241)
    # 9.3.3 - Maximum Range of constant altitude-airspeed (página 243)

    logger = get_logger()

    """
    Calcula o alcance de cruzeiro de uma aeronave a jato com base nos parâmetros da aeronave, altitude e peso.

    Parâmetros:
    - aircraft_parameters: Um dicionário contendo os parâmetros da aeronave, incluindo 'TSFC', 'WING_AREA', 'K', 'MTOW', 'OPERATIONAL_WEIGHT', 'MAX_PAYLOAD_WEIGHT', 'CD0', e 'CL_MAX'.
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
    - A função assume que a função get_cruise_velocity() está definida e disponível no escopo.
    """

    c = aircraft_parameters['TSFC']

    altitude = flight_parameters['CRUISE_ALTITUDE']
    logger.debug(f"Altitude: {altitude}")

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)['CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE

    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    logger.debug(f"V_cru: {V_cru}")

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']

    NP  = flight_parameters['NUMBER_OF_PASSENGERS']     # number of passengers
    FW  = flight_parameters['FUEL_WEIGHT']              # fuel weight
    CW  = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    sigma = aero.get_sigma(altitude=altitude)
    logger.debug(f"Sigma: {sigma}")

    MTOW = float(NP * aero.person_weight + OEW + FW + CW) if W_CRUISE is None else W_CRUISE
    logger.debug(f"MTOW: {MTOW}")

    # TODO: Revisar esta proporção no valor do zeta
    # If DeltaW is the weight of fuel consumed during the cruise

    W_1 = MTOW - 0.1 * FW
    logger.info(f"W_1: {W_1}")
    W_2 = MTOW - 0.9 * FW

    zeta = ((W_1 - W_2) / W_1) if zeta_CRUISE is None else zeta_CRUISE
    logger.info(f"Zeta: {zeta}")

    CD0 = aircraft_parameters['CD0']

    CL_cru = (2 * W_1) / (S * aero.rho_0 * sigma * V_cru ** 2)
    logger.debug(f"CL_cru: {CL_cru}")

    CD_cru = CD0 + K * CL_cru ** 2
    logger.debug(f"CD_cru: {CD_cru}")

    E_cru = CL_cru / CD_cru
    logger.debug(f"E_cru: {E_cru}")

    # -----------------------------------------------------------------------------------------------------------------#
    # CASE 1 - Range and Flight Parameters of Constant Altitude-Constant Lift Coefficient Flight
    x_h_CL = 2 * E_cru * V_cru * (1 - (1 - zeta) ** 0.5) / c
    E_m_h_CL = 1 / (2 * math.sqrt(K * CD0))
    # # Equação 9.16
    x_mr_h_CL = math.sqrt(3 * math.sqrt(3) * 0.5) * math.sqrt((2 * W_1/ S)/(aero.rho_0 * sigma)) * (math.sqrt(E_m_h_CL / CD0)/c) * (1 - math.sqrt(1 - zeta))
    # -----------------------------------------------------------------------------------------------------------------#
    # Case 2 - Range and Flight Parameters of Constant Airspeed-Constant Lift Coefficient Flight
    x_V_CL = ((E_cru * V_cru) / c) * math.log(1 / (1 - zeta))

    E_m_V_CL = 1 / (2 * math.sqrt(K * CD0))  # Equação 9.15 [OK]
    V1_Em = math.sqrt((2 * W_1 / S)/(aero.rho_0 * sigma)) * (K/CD0) ** 0.25  # Equação 9.15 [OK]

    E_mr_V_CL = math.sqrt(3) * E_m_V_CL / 2  # Equação 9.23 [OK]
    V_mr_V_CL = (3 ** 0.25) * V1_Em  # Equação 9.21 [OK]

    x_mr_V_CL = (E_mr_V_CL * V_mr_V_CL / c) * math.log(1 / (1 - zeta))  # Equação 9.24 [OK]
    # -----------------------------------------------------------------------------------------------------------------#
    # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight
    x_h_V = (2 * V_cru * E_cru) / c * math.atan(E_cru * zeta / (2 * E_cru * (1 - K * E_cru * CL_cru * zeta)))

    E_mr_h_V = math.sqrt(3) * E_m_V_CL / 2  # Equação 9.23
    zeta_rix = zeta

    # Equação 9.47
    x_mr_h_V = (
            ((1/c) * math.sqrt(2 * E_mr_h_V / CD0)) *
            math.sqrt((2 * W_1 * S) / (aero.rho_0 * sigma)) *
            ((3*(1 - zeta_rix)) ** 0.25) *
            math.atan((zeta * math.sqrt(3*(1 - zeta_rix))) / ((1 - zeta) + 3*(1 - zeta_rix))))

    ranges = {
        "RANGE_CONSTANT_HEIGHT_CL": round(x_h_CL, 2),
        "MAX_RANGE_CONSTANT_HEIGHT_CL": round(x_mr_h_CL, 2),

        "RANGE_CONSTANT_VELOCITY_CL": round(x_V_CL, 2),
        "MAX_RANGE_CONSTANT_VELOCITY_CL": round(x_mr_V_CL, 2),

        "RANGE_CONSTANT_HEIGHT_VELOCITY": round(x_h_V, 2),
        "MAX_RANGE_CONSTANT_HEIGHT_VELOCITY": round(x_mr_h_V, 2)
    }

    if plot:
        print_formatted_string(how="top")
        print_formatted_string(input_string=f'CRUISING JET RANGE', how="center")
        print_formatted_string()
        print_formatted_string(input_string=f'CASE 1 - ALTITUDE & CL CONSTANTS: {round(x_h_CL / 1000, 2)} [km]',
                               how="left")
        print_formatted_string(input_string=f'CASE 2 - VELOCITY & CL CONSTANTS: {round(x_V_CL / 1000, 2)} [km]',
                               how="left")
        print_formatted_string(input_string=f'CASE 3 - ALTITUDE & CL CONSTANTS: {round(x_h_V / 1000, 2)} [km]',
                               how="left")
        print_formatted_string(how="bottom")

    return ranges


# -------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------- ENDURANCE ----------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def cruising_jet_endurance(aircraft_parameters: dict, flight_parameters: dict, W_CRUISE=None, V_CRUISE=None, zeta_CRUISE=None, show=False):

    logger = get_logger()

    c = aircraft_parameters['TSFC']

    altitude = flight_parameters['CRUISE_ALTITUDE']

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)['CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE

    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    logger.debug(f"V_cru: {V_cru}")

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']

    NP  = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW  = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW  = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    sigma = aero.get_sigma(altitude=altitude)
    logger.debug(f"Sigma: {sigma}")

    MTOW = float(NP * aero.person_weight + OEW + FW + CW) if W_CRUISE is None else W_CRUISE
    logger.debug(f"MTOW: {MTOW}")

    W_1 = MTOW - 0.1 * FW
    logger.info(f"W_1: {W_1}")
    W_2 = MTOW - 0.9 * FW
    zeta = ((W_1 - W_2) / W_1) if zeta_CRUISE is None else zeta_CRUISE

    CD0 = aircraft_parameters['CD0']
    CL_cru = (2 * W_1) / (S * aero.rho_0 * sigma * V_cru ** 2)

    CD_cru = CD0 + K * CL_cru ** 2
    E_cru = CL_cru / CD_cru

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 1 - Range and Flight Parameters of Constant Altitude-Constant Lift Coefficient Flight
    t_h_CL = (E_cru / c) * math.log(1 / (1 - zeta))

    E_t_m_h_CL = 1 / (2 * math.sqrt(K * CD0))
    t_m_h_CL = (E_t_m_h_CL / c) * math.log(1 / (1 - zeta))  # Equação 9.79 [OK]

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 2 - Range and Flight Parameters of Constant Airspeed-Constant Lift Coefficient Flight
    t_V_CL = (E_cru / c) * math.log(1 / (1 - zeta))

    E_t_m_V_CL = 1 / (2 * math.sqrt(K * CD0))
    t_m_V_CL = (E_t_m_V_CL / c) * math.log(1 / (1 - zeta))

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight
    t_h_V = (2 * E_cru / c) * math.atan((E_cru * zeta) / (2 * E_cru * (1 - K * E_cru * CL_cru * zeta)))

    zeta_rix = zeta
    E_t_m_h_V = 1 / (2 * math.sqrt(K * CD0))
    # Equação 9.85
    t_m_h_V = (
        (2 * E_t_m_h_V / c) *
        math.atan((zeta * math.sqrt(1 - zeta_rix)) / ((1 - zeta) + (1 - zeta_rix)))
    )



    endurance = {
        "ENDURANCE_CONSTANT_HEIGHT_CL": t_h_CL,
        "MAX_ENDURANCE_CONSTANT_HEIGHT_CL": t_m_h_CL,

        "ENDURANCE_CONSTANT_VELOCITY_CL": t_V_CL,
        "MAX_ENDURANCE_CONSTANT_VELOCITY_CL": t_m_V_CL,

        "ENDURANCE_CONSTANT_HEIGHT_VELOCITY": t_h_V,
        "MAX_ENDURANCE_CONSTANT_HEIGHT_VELOCITY": t_m_h_V
    }

    if show:
        print_formatted_string(how="top")
        print_formatted_string(input_string=f'CRUISING JET ENDURANCE', how="center")
        print_formatted_string()
        print_formatted_string(input_string=f'CASE 1 - ALTITUDE & CL CONSTANTS: {round(t_h_CL / 3600, 2)} [h]',
                               how="left")
        print_formatted_string(input_string=f'CASE 2 - VELOCITY & CL CONSTANTS: {round(t_V_CL / 3600, 2)} [h]',
                               how="left")
        print_formatted_string(input_string=f'CASE 3 - ALTITUDE & CL CONSTANTS: {round(t_h_V / 3600, 2)} [h]',
                               how="left")
        print_formatted_string(how="bottom")

    return endurance


# -------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------- PAYLOAD x RANGE -------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def payload_x_range(aircraft_parameters: dict, flight_parameters: dict):

    #TODO: Ajustar esta função

    n = aircraft_parameters['TSFC']
    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']

    W = 1 #TODO: revizar este peso

    altitude = flight_parameters['CRUISE_ALTITUDE']  # Cruise Height
    h_cru = altitude
    V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    PW = flight_parameters['PAYLOAD_WEIGHT']  # payload weight (CW + 80*NP)
    OEW = aircraft_parameters['OEW']

    def range_iter(W_1, zeta):

        range_list = []

        for V_i in linspace(V_cru - 50, V_cru + 50, 20):
            for h_i in linspace(h_cru - 2000, h_cru + 2000, 10):

                rho_i = aero.get_density(altitude=h_i)

                CL_i = (2 * W_1) / (S * rho_i * V_i ** 2)
                CD_i = CD0 + K * CL_i ** 2
                E_i = CL_i / CD_i

                # CASE 1 - Range and Flight Parameters of Constant Altitude-Constant Lift Coefficient Flight
                x_h_CL = 2 * E_i * V_i * (1 - (1 - zeta) ** 0.5) / n
                # -----------------------------------------------------------------------------------------------------------------#
                # Case 2 - Range and Flight Parameters of Constant Airspeed-Constant Lift Coefficient Flight
                x_V_CL = ((E_i * V_i) / n) * math.log(1 / (1 - zeta))
                # -----------------------------------------------------------------------------------------------------------------#
                # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight
                x_h_V = (2 * V_cru * E_i) / n * math.atan(E_i * zeta / (2 * E_i * (1 - K * E_i * CL_i * zeta)))

                range_list.append(max(x_h_CL, x_V_CL, x_h_V))

        return max(range_list)

    MTOW               = float(NP * aero.person_weight + OEW + FW + PW)
    MAX_FUEL_WEIGHT    = FW
    OPERATIONAL_WEIGHT = OEW
    MAX_PAYLOAD_WEIGHT = PW

    aux1 = MAX_FUEL_WEIGHT - (MTOW - (OPERATIONAL_WEIGHT + MAX_PAYLOAD_WEIGHT))  # Combustível excedente

    aux2 = MAX_PAYLOAD_WEIGHT - aux1  # Carga Paga no ponto C

    # Alcance nos pontos principais:
    x_A = 0
    x_B = range_iter(W_1=MTOW, zeta=(MTOW - (OPERATIONAL_WEIGHT + MAX_PAYLOAD_WEIGHT)) / MTOW)
    x_C = range_iter(W_1=MTOW, zeta=MAX_FUEL_WEIGHT / MTOW)
    x_D = range_iter(W_1=MTOW - aux2, zeta=MAX_FUEL_WEIGHT / (MTOW - aux2))

    # Ponto A:
    A = [x_A / 1000, MAX_PAYLOAD_WEIGHT / 1000]
    # Ponto B:
    B = [x_B / 1000, MAX_PAYLOAD_WEIGHT / 1000]
    # Ponto C:
    C = [x_C / 1000, aux2 / 1000]
    # Ponto D:
    D = [x_D / 1000, 0 / 1000]

    plt.ylabel("Payload [kN]", fontsize=12)
    plt.title("Diagram Payload vs. Range", fontsize=14)
    plt.xlabel("x [km]", fontsize=12)
    plt.grid(True)

    plt.plot([A[0], B[0]], [A[1], B[1]], linewidth=2.5, c="#1D3D7B")
    plt.plot([B[0], C[0]], [B[1], C[1]], linewidth=2.5, c="#1D3D7B")
    plt.plot([C[0], D[0]], [C[1], D[1]], linewidth=2.5, c="#1D3D7B")

    plt.scatter(A[0], A[1], c="#1D3D7B")
    plt.scatter(B[0], B[1], c="#1D3D7B")
    plt.scatter(C[0], C[1], c="#1D3D7B")
    plt.scatter(D[0], D[1], c="#1D3D7B")

    plt.show()


aircraft_parameters_dict = {
    "WING_AREA":  50.4,
    "CL_MAX": 1.8,
    "CD0": 0.0171,
    "K": 0.042,
    "MTOW": 21071,
    "MAX_PAYLOAD_WEIGHT": 907,
    "ZERO_THRUST": 8e5,
    "TSFC": 1,  # Thrust specific fuel consumption. It measures how much fuel the engine burns each hour.,
    'MAX_FUEL_WEIGHT': 8149,
    'OPERATIONAL_WEIGHT': 11560
}


# cruising_jet_range(aircraft_parameters, show = True)
# cruising_jet_endurance(aircraft_parameters, show=True)
# payload_x_range(aircraft_parameters=aircraft_parameters_dict, W=aircraft_parameters_dict['MTOW'], altitude=11582.4)

# V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters_dict, W=2.7e6, altitude=11582.4)
# print(V_cru)

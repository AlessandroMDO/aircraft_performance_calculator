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
from .utils import hash_dict, print_formatted_string, deep_freeze_args
import matplotlib.pyplot as plt
# from aero import Aero
import math
import numpy as np
from functools import lru_cache
from .aero import Aero


aero = Aero()

def get_cruise_velocity(aircraft_parameters: dict, flight_parameters: dict, plot=False):

    """
        Calcula a velocidade de cruzeiro de uma aeronave com base nos parâmetros da aeronave, altitude e peso.

        Parâmetros:
        - aircraft_parameters: Um dicionário contendo os parâmetros da aeronave, incluindo 'ZERO_THRUST', 'SURFACE_AREA', 'CD0', 'K', 'THRUST_FACTOR', e 'CL_MAX'.
        - altitude: Altitude em metros.
        - W: Peso da aeronave em Newtons. #TODO qual peso usar aqui?
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

    #todo: revizar este peso (MTOW - 50% do combustível ?)
    MTOW = float(NP * aero.person_weight + OEW + FW + CW)
    W = MTOW - 0.5 * FW  # MTOW - (50% do combustível)

    T = T0 * aircraft_parameters['NE']

    T_CRU = aero.calculate_general_thrust(altitude=altitude, sea_level_thrust=T, thrust_factor=n)

    E_m = 1 / (2 * math.sqrt(K * CD0))

    V_1 = ((T_CRU * (sigma ** n))/(sigma * rho_0 * S * CD0)) * (1 + math.sqrt(1 - (1/E_m ** 2)*((W**2)/(T_CRU * sigma**n)**2)))
    V_2 = ((T_CRU * (sigma ** n))/(sigma * rho_0 * S * CD0)) * (1 - math.sqrt(1 - (1/E_m ** 2)*((W**2)/(T_CRU * sigma**n)**2)))

    V_cru_1 = math.sqrt(max(V_1, 0))
    V_cru_2 = math.sqrt(max(V_2, 0))

    V_S = aero.calculate_stall_velocity(W=W, CL_max=CL_max, S=S, rho=rho_0)

    # Selecionamos a maior velocidade de cruzeiro
    V_cru = max(V_cru_1, V_cru_2) if (V_cru_1 > V_S and V_cru_2 > V_S) else V_cru_1 if (V_cru_1 > V_S > V_cru_2) else V_cru_2

    if plot is False:
        return V_cru
    else:

        lista_arrasto_total    = []
        lista_arrasto_parasita = []
        lista_arrasto_induzido = []

        v_range = np.linspace(max(V_cru - 500, 100), V_cru + 100, 50)

        for v in v_range:

            #TODO: revizar esses arrastos
            arrasto_parasita = 0.5 * sigma * rho_0 * (v ** 2) * S * CD0
            arrasto_induzido = (2 * K * W ** 2) / (sigma * rho_0 * S * v ** 2)

            arrasto_total = arrasto_parasita + arrasto_induzido

            lista_arrasto_total.append(arrasto_total)
            lista_arrasto_parasita.append(arrasto_parasita)
            lista_arrasto_induzido.append(arrasto_induzido)

        #TODO: o arrasto mínimo deveria ocorrer na velocidade de cruzeiro ?!
        fig_cruzeiro = plt.figure(figsize=(5, 3))
        plt.plot(v_range, [i / 1e3 for i in lista_arrasto_total], c='black', label="Arrasto Total")
        plt.plot(v_range, [i / 1e3 for i in lista_arrasto_parasita], c='black', ls='--', label="Arrasto Parasita")
        plt.plot(v_range, [i / 1e3 for i in lista_arrasto_induzido], c='black', ls='-.', label="Arrasto Induzido")
        plt.plot(v_range, [T_CRU / 1e3] * len(v_range), label="Empuxo", ls=(0, (5, 10)), color='black')
        plt.scatter(v_range[lista_arrasto_total.index(min(lista_arrasto_total))], min(lista_arrasto_total) / 1e3, c='black', label="Arrasto Mínimo")
        plt.xlabel("Velocidade [m/s]", size=12)
        plt.ylabel("Arrasto [kN]", size=12)
        plt.title("Relação empuxo e arrasto por velocidade")
        plt.grid()
        plt.legend()
        plt.show()

        return V_cru, fig_cruzeiro










def cruising_jet_range(aircraft_parameters: dict, flight_parameters: dict, show=False):

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

    V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)
    h_cru = altitude  # Cruise Height

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    PW = flight_parameters['PAYLOAD_WEIGHT']  # payload weight
    OEW = aircraft_parameters['OEW']

    #TODO: revisar
    W_1 = float(NP * aero.person_weight + OEW + FW + PW)
    W_2 = OEW + PW

    zeta = (W_1 - W_2) / W_1

    rho_cru = aero.get_density(altitude=h_cru)

    CD0 = aircraft_parameters['CD0']
    CL_cru = (2 * W_1) / (S * rho_cru * V_cru ** 2)
    CD_cru = CD0 + K * CL_cru ** 2
    E_cru = CL_cru / CD_cru

    # -----------------------------------------------------------------------------------------------------------------#
    # CASE 1 - Range and Flight Parameters of Constant Altitude-Constant Lift Coefficient Flight
    x_h_CL = 2 * E_cru * V_cru * (1 - (1 - zeta) ** 0.5) / c
    # -----------------------------------------------------------------------------------------------------------------#
    # Case 2 - Range and Flight Parameters of Constant Airspeed-Constant Lift Coefficient Flight
    x_V_CL = ((E_cru * V_cru) / c) * math.log(1 / (1 - zeta))
    # -----------------------------------------------------------------------------------------------------------------#
    # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight
    x_h_V = (2 * V_cru * E_cru) / c * math.atan(E_cru * zeta / (2 * E_cru * (1 - K * E_cru * CL_cru * zeta)))

    # [m]
    ranges = {
        "range_constant_height_cl": round(x_h_CL, 2),
        "range_constant_velocity_cl": round(x_V_CL, 2),
        "range_constant_height_velocity": round(x_h_V, 2)
    }

    if show:
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


def cruising_jet_endurance(aircraft_parameters: dict, flight_parameters: dict, show=False):

    c = aircraft_parameters['TSFC']

    altitude = flight_parameters['CRUISE_ALTITUDE'] # Cruise Height

    V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, altitude=altitude)
    h_cru = altitude

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']

    W_1 = aircraft_parameters['MTOW']  #TODO: fix MTOW
    W_2 = aircraft_parameters['OEW'] + aircraft_parameters['MAX_PAYLOAD_WEIGHT'] #TODO: fix MAX_PAYLOAD_WEIGHT
    zeta = (W_1 - W_2) / W_1

    atmosphere_cru = aero.get_density(altitude=h_cru)
    rho_cru = atmosphere_cru.density[0]

    CD0 = aircraft_parameters['CD0']
    CL_cru = (2 * W_1) / (S * rho_cru * V_cru ** 2)

    CD_cru = CD0 + K * CL_cru ** 2
    E_cru = CL_cru / CD_cru

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 1 - Range and Flight Parameters of Constant Altitude-Constant Lift Coefficient Flight
    t_h_CL = (E_cru / c) * math.log(1 / (1 - zeta))

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 2 - Range and Flight Parameters of Constant Airspeed-Constant Lift Coefficient Flight
    t_V_CL = (E_cru / c) * math.log(1 / (1 - zeta))

    # -----------------------------------------------------------------------------------------------------------------#
    # Case 3 - Range of Flight Parameters of Constant Altitude-Constant Airspeed Flight
    t_h_V = (2 * E_cru / c) * math.atan((E_cru * zeta) / (2 * E_cru * (1 - K * E_cru * CL_cru * zeta)))

    # [s]
    endurance = {
        "endurance_constant_height_cl": t_h_CL,
        "endurance_constant_velocity_cl": t_V_CL,
        "endurance_constant_height_velocity": t_h_V
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

    n = aircraft_parameters['TSFC']
    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']

    W = 1 #TODo: revizar este peso

    altitude = flight_parameters['CRUISE_ALTITUDE']  # Cruise Height
    h_cru = altitude
    V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    PW = flight_parameters['PAYLOAD_WEIGHT']  # payload weight (CW + 80*NP)
    OEW = aircraft_parameters['OEW']

    def range_iter(W_1, zeta):

        range_list = []

        for V_i in np.linspace(V_cru - 50, V_cru + 50, 20, endpoint=True):
            for h_i in np.linspace(h_cru - 2000, h_cru + 2000, 10, endpoint=True):

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

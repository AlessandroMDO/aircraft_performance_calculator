import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import sys
sys.path.append('functions')
from functions.aero import Aero
from functions.utils import *
from functions.cruising_jet import get_cruise_velocity
from numpy import linspace
import matplotlib.pyplot as plt
from functools import lru_cache
import math

c = Aero()


def gliding_angle_rate_of_descent(aircraft_parameters, flight_parameters, altitude, plot=False):
    """
    Calcula o ângulo de planagem e a taxa de descida de uma aeronave em planagem em uma determinada altitude.

    Parâmetros:
    - aircraft_parameters: Um dicionário contendo os parâmetros da aeronave, incluindo 'CD0', 'S', 'K', e 'MTOW'.
    - altitude: Altitude em metros.
    - plot: Um sinalizador booleano que indica se os resultados devem ser exibidos (opcional, padrão é False).

    Retorna:
    Um dicionário contendo dois resultados:
    - "GLIDING_ANGLE": Ângulo de planagem em radianos.
    - "GLIDING_RATE_OF_DESCENT": Taxa de descida em metros por segundo.

    Se plot for True, também retorna dois gráficos:
    - "GLIDING_ANGLE_PLOT": Gráfico do ângulo de planagem em função da velocidade de planagem.
    - "GLIDING_RATE_OF_DESCENT_PLOT": Gráfico da taxa de descida em função da velocidade de planagem.

    Notas:
    - A função assume que a função get_cruise_velocity() está definida e disponível no escopo.
    - O parâmetro 'K' pode ser calculado em função de outros parâmetros como 'e' e 'AR'.
    - O peso 'W' considerado deve ser definido claramente (ex: MTOW).
    """

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    PW = flight_parameters['PAYLOAD_WEIGHT']  # payload weight
    OEW = aircraft_parameters['OEW']

    MTOW = float(NP * c.person_weight + OEW + FW + PW)
    W = MTOW - 0.5 * FW  # MTOW - (50% do combustível)

    CD0 = aircraft_parameters['CD0']
    S   = aircraft_parameters['S']
    K = aircraft_parameters['K']

    V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)

    sigma = c.get_sigma(altitude=altitude)
    rho_ssl = c.rho_0

    part_1 = (rho_ssl * sigma * V_cru ** 2 * CD0) / (2 * W / S)
    print(part_1)

    part_2 = (2 * K * (W / S)) / (rho_ssl * sigma * V_cru ** 2)
    print(part_2)

    gliding_angle_cru = -1 * (part_1 + part_2)
    rate_of_descent_cru = - 1 * V_cru * gliding_angle_cru

    if plot is False:
        return {"GLIDING_ANGLE": gliding_angle_cru, "GLIDING_RATE_OF_DESCENT": rate_of_descent_cru}
    else:
        velocity_range = linspace(0.7 * V_cru, 1.3 * V_cru, 25)
        gliding_angle_list = []
        for v_i in velocity_range:
            gliding_i = -1 * (((rho_ssl * sigma * v_i ** 2 * CD0) / (2 * W / S)) + (2 * K * (W / S)) / (rho_ssl * sigma * v_i ** 2))
            gliding_angle_list.append(gliding_i)

        rate_descent_list = [-1 * v * gamma for v, gamma in zip(velocity_range, gliding_angle_list)]

        fig_rate_of_descent = plt.figure(figsize=(5, 3))
        plt.plot(velocity_range, rate_descent_list, c='black', label = "Rate of descent")
        plt.axvline(x=V_cru, ymin = 0, ymax = 1, color='r', label = "Cruise Velocity")
        plt.xlabel("Velocity [m/s]", size=12)
        plt.ylabel("Rate [m/s]", size=12)
        plt.title("Rate of descent per gliding velocity")
        plt.grid()
        plt.legend()
        plt.show()

        fig_gliding_angle = plt.figure(figsize=(5, 3))
        plt.plot(velocity_range, gliding_angle_list, c='black', label = "Gliding angle")
        plt.axvline(x=V_cru, ymin = 0, ymax = 1, color='r', label = "Cruise Velocity")
        plt.xlabel("Velocity [m/s]", size=12)
        plt.ylabel("Gliding Angle [rad]", size=12)
        plt.title("Gliding angle per gliding velocity")
        plt.grid()
        plt.legend()
        plt.show()

        return {
            "GLIDING_ANGLE": gliding_angle_cru,
            "GLIDING_ANGLE_PLOT": fig_gliding_angle,
            "GLIDING_RATE_OF_DESCENT": rate_of_descent_cru,
            "GLIDING_RATE_OF_DESCENT_PLOT": fig_rate_of_descent
        }


def gliding_range_endurance(aircraft_parameters, flight_parameters, W=None, V_cru=None, graph=False):

    """
    Calcula o alcance e a autonomia de uma aeronave em planagem entre duas altitudes.

    Parâmetros:
    - aircraft_parameters: Um dicionário contendo os parâmetros da aeronave, incluindo 'SURFACE_AREA', 'CL_MAX', 'CD0', 'K', e 'MTOW'.
    - altitude_final: Altitude inicial em metros.
    - altitude_inicial: Altitude final em metros.

    Retorna:
    Um dicionário contendo duas categorias de resultados:
    1. Para voo com coeficiente de sustentação constante:
        - "GLIDING_RANGE_CONSTANT_LIFT": Alcance em metros.
        - "GLIDING_ENDURANCE_CONSTANT_LIFT": Autonomia em segundos.

    2. Para voo com velocidade constante e coeficiente de sustentação variável:
        - "GLIDING_RANGE_CONSTANT_AIRSPEED": Alcance em metros.
        - "GLIDING_ENDURANCE_CONSTANT_AIRSPEED": Autonomia em segundos.

    Notas:
    - A função assume que as funções get_cruise_velocity() e calculate_general_drag_coefficient() estão definidas e disponíveis no escopo.
    - O parâmetro 'K' pode ser calculado em função de outros parâmetros como 'e' e 'AR'.
    - O peso 'W' considerado deve ser definido claramente (ex: MTOW).
    """

    S = aircraft_parameters['S']
    CL_max = aircraft_parameters['CL_MAX']
    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    PW = flight_parameters['PAYLOAD_WEIGHT']  # payload weight
    OEW = aircraft_parameters['OEW']

    MTOW = float(NP * c.person_weight + OEW + FW + PW)

    # MTOW - (50% do combustível)
    W = MTOW - 0.5 * FW if W is None else W

    beta = 9296

    altitude_final   = flight_parameters['landing_parameters']['ALTITUDE_LANDING']
    altitude_inicial = flight_parameters['CRUISE_ALTITUDE']

    rho_ssl = c.rho_0

    def gliding_range_endurance_constant_lift():
        """
        Cálculo do alcance máximo para CL constante.
        1. Por padrão , o CL adotado é o CL máximo.
        2. Também é calculado o alcance máximo, assim como a autonomia deste alcance máximo.
            2.1 Para obter o alcance máximo, o CL e o CD são definidos como:
                CL = ((CD0 / K)  ** 0.5)
                CD = (2 * CD0)
        3. É plotado um gráfico de alcance x CL para uma determinada altitude

        Returns: dicionário contendo o resultado

        """
        CD = c.calculate_general_drag_coefficient(CD0=CD0, K=K, CL=CL_max)
        E_st = CL_max / CD

        CL_max_range_cond = (CD0 / K) ** 0.5
        CD_max_range_cond = (2 * CD0)
        E_max_range = CL_max_range_cond / CD_max_range_cond

        CL_max_endurance_cond = (3 * CD0 / K) ** 0.5
        CD_max_endurance_cond = 4 * CD0
        E_max_endurance = CL_max_endurance_cond / CD_max_endurance_cond

        def get_x_cl(E_i):
            x_cl = E_i * (altitude_inicial - altitude_final)
            return x_cl

        def get_t_cl(E_i, CL_i):
            t_cl = (2 * beta * E_i * ((rho_ssl * CL_i) / (2 * W / S))**0.5) * (math.e ** (-altitude_final/(2*beta)) - math.e ** (-altitude_inicial/(2*beta)))
            return t_cl

        # Caso padrão (1)
        x_cl_st = get_x_cl(E_i=E_st)
        t_cl_st = get_t_cl(E_i=E_st, CL_i=CL_max)

        # Caso de alcance máximo (2)
        x_cl_max_range = get_x_cl(E_i=E_max_range) # Alcance máximo
        t_cl_max_range = get_t_cl(E_i=E_max_range, CL_i=CL_max_range_cond)  # Autonomia do alcance máximo
        
        # Caso de endurance máximo (3)

        t_cl_max_endurance = get_t_cl(E_i=E_max_endurance, CL_i=CL_max_endurance_cond)  # Autonomia máxima
        x_cl_max_endurance = get_x_cl(E_i=E_max_endurance)  # Alcance máximo da autonomia máxima


        if graph is True:
            # Gráfico (3)
            CL_i_list, x_cl_i_list, t_cl_i_list = [], [], []

            for CL_i in linspace(0.1 * min(CL_max, CL_max_range_cond, CL_max_endurance_cond), 1.2 * max(CL_max, CL_max_range_cond, CL_max_endurance_cond), 20):

                CD_i = c.calculate_general_drag_coefficient(CD0=CD0, K=K, CL=CL_i)
                E_i = CL_i / CD_i

                x_cl_i = get_x_cl(E_i=E_i)
                t_cl_i = get_t_cl(E_i=E_i, CL_i=CL_i)

                CL_i_list.append(CL_i)
                x_cl_i_list.append(x_cl_i)
                t_cl_i_list.append(t_cl_i)

            # TODO: ajustar cores
            fig_cl_constant, ax_cl_constant = plt.subplots(figsize=(5, 3))

            fig1 = ax_cl_constant.plot(CL_i_list, [t/3600 for t in t_cl_i_list], c='blue', marker='o', label="Endurance", ls='--')
            ax_cl_constant.set_xlabel("Lit Coefficient [-]", fontsize=14)
            ax_cl_constant.set_ylabel('Time [h]', color="black", fontsize=14)

            fig2 = ax_cl_constant.axvline(CL_max, c='black', label="CLmax")
            fig6 = ax_cl_constant.scatter(CL_max_range_cond, t_cl_max_range / 3600, label="Endurance of the maximum range", marker='x', color='black')

            fig7 = ax_cl_constant.scatter(CL_max_endurance_cond, t_cl_max_endurance / 3600, label="Maximum Endurance", marker='+', color='green')

            ax2 = ax_cl_constant.twinx()
            fig3 = ax2.plot(CL_i_list, [x/1000 for x in x_cl_i_list], c='black', marker='o', label="Range")
            ax2.set_ylabel('Range [km]', color="black", fontsize=14)

            fig4 = ax_cl_constant.scatter(CL_i_list[-1], t_cl_i_list[-1] / 2500, alpha=0)
            fig5 = ax2.scatter(CL_max_range_cond, x_cl_max_range / 1000, label="Maximum Range", marker ='x', color='black')

            fig8 = ax2.scatter(CL_max_endurance_cond, x_cl_max_endurance / 1000, label="Range of the maximum endurance", marker='+', color='red')

            lines, labels = ax_cl_constant.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc=0)

            plt.title(f"Range [km] & Endurance [h] per Lift Coefficient [-]\nfrom h2 = {altitude_inicial / 1000} [km] to h1 = {altitude_final / 1000} [km]", fontsize = 12)
            ax_cl_constant.grid()
            plt.show()

        result = {
            "GLIDING_RANGE_CONSTANT_LIFT_STANDARD": round(x_cl_st, 2),
            "GLIDING_ENDURANCE_CONSTANT_LIFT_STANDARD": round(t_cl_st, 2),

            "GLIDING_MAX_RANGE_CONSTANT_LIFT": round(x_cl_max_range, 2),
            "GLIDING_ENDURANCE_MAX_RANGE_CONSTANT_LIFT_MAX": round(t_cl_max_range, 2),

            "GLIDING_MAX_ENDURANCE_CONSTANT_LIFT": round(t_cl_max_endurance, 2),
            "GLIDING_RANGE_MAX_ENDURANCE_CONSTANT_LIFT": round(x_cl_max_endurance, 2)

        }
        return result

    def gliding_range_endurance_constant_airspeed():

        V = get_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters) if V_cru is None else V_cru
        # B = (2 * K * (W / S)) / (rho_ssl * V ** 2)

        def get_A_B(CD0_i, V_i):

            A = (rho_ssl * CD0_i * V_i ** 2) / (2 * W/S)
            B = (2 * K * (W / S)) / (rho_ssl * V_i ** 2)
            return A, B

        def get_x_v(CD0_i, A_i, B_i):

            part_1_range = math.atan((A_i / B_i) * math.e ** (-altitude_final / beta))
            part_2_range = math.atan((A_i / B_i) * math.e ** (-altitude_inicial / beta))

            x_v = ((beta / B_i) * (part_1_range - part_2_range))

            return x_v

        def get_t_v(CD0_i, V_i):

            part_1_endurance = math.atan((CD0_i * rho_ssl ** 2 * (V_i ** 4) * math.e ** (-altitude_final / beta)) / (4 * K * (W/S) ** 2))
            part_2_endurance = math.atan((CD0_i * rho_ssl ** 2 * (V_i ** 4) * math.e ** (-altitude_inicial / beta)) / (4 * K * (W/S) ** 2))

            t_v = ((beta * rho_ssl * V_i) / (2 * K * W / S)) * (part_1_endurance - part_2_endurance)

            return t_v

        # Caso padrão (1)
        A_st, B_st = get_A_B(CD0_i=CD0, V_i=V_cru)
        x_v_st = get_x_v(CD0_i=CD0, A_i=A_st, B_i=B_st)
        t_v_st = get_t_v(CD0_i=CD0, V_i=V_cru)

        # Caso máximo alcance (2)
        V_max_range = ((3 ** 0.5 * K) / CD0) ** 0.25 * (2 * (W / S) / rho_ssl) ** 0.5 * math.e ** ((altitude_inicial + altitude_final) / (8 * beta))
        A_v_max_range, B_v_max_range = get_A_B(CD0_i=CD0, V_i=V_max_range)
        x_v_max_range = get_x_v(CD0_i=CD0, A_i=A_v_max_range, B_i=B_v_max_range)
        t_v_max_range = x_v_max_range / V_max_range # Ou get_t_v(CD0_i=CD0, V_i=V_max_range)



        # Caso máxima autonomia (3)
        # TODO

        if graph is True:
            V_i_list, x_v_i_list, t_v_i_list = [], [], []









        result = {
            "GLIDING_RANGE_CONSTANT_AIRSPEED": round(x_v_st, 2),
            "GLIDING_ENDURANCE_CONSTANT_AIRSPEED": round(t_v_st, 2),

            "GLIDING_MAX_RANGE_CONSTANT_AIRSPEED" : round(x_v_max_range, 2),
            "GLIDING_ENDURANCE_MAX_RANGE_CONSTANT_AIRSPEED": round(t_v_max_range, 2)

        }

        return result

    results_gliding_range_endurance = {
        "GLIDING_CONSTANT_LIFT": gliding_range_endurance_constant_lift(),
        "GLIDING_CONSTANT_AIRSPEED": gliding_range_endurance_constant_airspeed(),
    }

    return results_gliding_range_endurance



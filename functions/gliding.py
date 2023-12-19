from functions.aero import Aero
from functions.utils import *
from functions.cruising_jet import get_cruise_velocity
from numpy import linspace
import matplotlib.pyplot as plt
from functools import lru_cache
import math

c = Aero()


def gliding_angle_rate_of_descent(aircraft_parameters, altitude, plot=False):
    """
    Calcula o ângulo de planagem e a taxa de descida de uma aeronave em planagem em uma determinada altitude.

    Parâmetros:
    - aircraft_parameters: Um dicionário contendo os parâmetros da aeronave, incluindo 'CD0', 'SURFACE_AREA', 'K', e 'MTOW'.
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

    CD0 = aircraft_parameters['CD0']
    S   = aircraft_parameters['SURFACE_AREA']

    # TODO: K deve ser calculado em função de e, AR
    K   = aircraft_parameters['K']

    # TODO: qual peso considerar ? MTOW ?
    W = aircraft_parameters['K']

    V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, altitude=altitude, W=W)

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
        plt.axvline(x = V_cru, ymin = 0, ymax = 1, color='r', label = "Cruise Velocity")
        plt.xlabel("Velocity [m/s]", size=12)
        plt.ylabel("Rate [m/s]", size=12)
        plt.title("Rate of descent per gliding velocity")
        plt.grid()
        plt.legend()
        plt.show()

        fig_gliding_angle = plt.figure(figsize=(5, 3))
        plt.plot(velocity_range, gliding_angle_list, c='black', label = "Gliding angle")
        plt.axvline(x = V_cru, ymin = 0, ymax = 1, color='r', label = "Cruise Velocity")
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


def gliding_range_endurance(aircraft_parameters, altitude_final, altitude_inicial):

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

    S = aircraft_parameters['SURFACE_AREA']
    CL_max = aircraft_parameters['CL_MAX']
    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K'] # TODO: K deve ser calculado em função de e, AR
    # TODO: qual peso considerar ? MTOW ?
    W = aircraft_parameters['K']

    beta = 9296

    V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, altitude=altitude_final, W=W)

    rho_ssl = c.rho_0

    def gliding_range_endurance_constant_lift():

        CD = c.calculate_general_drag_coefficient(CD0=CD0, K=K, CL=CL_max)
        E = CL_max / CD

        x_cl = E * (altitude_inicial - altitude_final)
        t_cl = (2 * beta * E * ((rho_ssl * CL_max) / (2 * W / S))**0.5) * (math.e ** (-altitude_final/(2*beta)) - math.e ** (-altitude_inicial/(2*beta)))

        return {"GLIDING_RANGE_CONSTANT_LIFT": round(x_cl, 2), "GLIDING_ENDURANCE_CONSTANT_LIFT": round(t_cl, 2)}

    def gliding_range_endurance_constant_airspeed():

        A = (rho_ssl * CD0 * V_cru ** 2) / (2 * W/S)
        B = (2 * K * (W/S)) / (rho_ssl * V_cru ** 2)

        part_1_range = math.atan((A/B) * math.e ** (-altitude_final/beta))
        part_2_range = math.atan((A/B) * math.e ** (-altitude_inicial/beta))

        x_v = ((beta / B) * (part_1_range - part_2_range))

        part_1_endurance = math.atan((CD0 * rho_ssl ** 2 * (V_cru ** 4) * math.e ** (-altitude_final / beta)) / (4 * K * (W/S) ** 2))
        part_2_endurance = math.atan((CD0 * rho_ssl ** 2 * (V_cru ** 4) * math.e ** (-altitude_inicial / beta)) / (4 * K * (W/S) ** 2))

        t_v = ((beta * rho_ssl * V_cru) / (2 * K * W / S)) * (part_1_endurance - part_2_endurance)

        return {"GLIDING_RANGE_CONSTANT_AIRSPEED": round(x_v, 2), "GLIDING_ENDURANCE_CONSTANT_AIRSPEED": round(t_v, 2)}

    results_gliding_range_endurance = {
        "GLIDING_CONSTANT_LIFT": gliding_range_endurance_constant_lift(),
        "GLIDING_CONSTANT_AIRSPEED": gliding_range_endurance_constant_airspeed(),
    }

    return results_gliding_range_endurance

# TODO: K deve ser calculado em função de e, AR
aircraft_parameters = {
    "CD0": 0.7,
    "SURFACE_AREA": 50.4,
    "K": 0.5,
    "W": 169998,
    "ZERO_THRUST": 44482 * 2,
    "THRUST_FACTOR": 0.1,
    "CL_MAX": 1.8,
}

results = gliding_range_endurance(aircraft_parameters=aircraft_parameters, altitude_final=0, altitude_inicial=11000)
print(results)


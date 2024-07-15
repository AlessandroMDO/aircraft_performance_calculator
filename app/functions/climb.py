import math
from .aero import Aero
from .utils import get_logger, linspace
from functions.cruising_jet import calc_cruise_velocity
import matplotlib.pyplot as plt
from numpy import polyfit, polyval

aero = Aero()


def get_climb_parameters(altitude):
    """
    Obtém os parâmetros de subida de uma aeronave com base na altitude.

    Parâmetros:
    altitude (float): Altitude em metros (m) para a qual os parâmetros de subida são determinados.

    Retorna:
    dict: Dicionário contendo os parâmetros de subida:
        - "e" (float): Fator de eficiência de subida.
        - "h_rix" (float): Altitude de referência em metros (m).
        - "beta" (float): Parâmetro beta de subida em metros (m).

    Os parâmetros são determinados com base na altitude fornecida:
    - Para altitudes até 11.000 metros, os valores são: e = 1, h_rix = 0, beta = 9296.
    - Para altitudes acima de 11.000 metros, os valores são: e = 0.3063, h_rix = 11000, beta = 6216.
    """

    if altitude <= 11000:
        e = 1
        h_rix = 0
        beta = 9296
    else:
        e = 0.3063
        h_rix = 11000
        beta = 6216

    return {
        "e": e,
        "h_rix": h_rix,
        "beta": beta
    }


def calc_max_climb_angle_rate_of_climb(aircraft_parameters: dict, flight_parameters: dict,
                                       ALTITUDE_GLI=None, V_CRUISE=None,
                                       plot=False, display=False):
    """
    Calcula o ângulo máximo de subida (gamma_max) e a taxa máxima de subida (h_max) de uma aeronave.

    Parâmetros:
    aircraft_parameters (dict): Dicionário contendo os parâmetros da aeronave.
        - 'OEW' (float): Peso operacional vazio da aeronave em Newton (N).
        - 'CD0' (float): Coeficiente de arrasto de arrasto parasita (adimensional).
        - 'K' (float): Coeficiente de arrasto induzido (adimensional).
        - 'S' (float): Área da asa (m²).
        - 'T0' (float): Empuxo ao nível do mar por motor em Newtons (N).
        - 'NE' (int): Número de motores.
        - 'TSFC' (float): Consumo específico de combustível por empuxo em kg/N.s.
        - 'E_m' (float): Eficiência aerodinâmica máxima (adimensional).
    flight_parameters (dict): Dicionário contendo os parâmetros do voo.
        - 'NUMBER_OF_PASSENGERS' (int): Número de passageiros.
        - 'FUEL_WEIGHT' (float): Peso do combustível em Newton (N).
        - 'DISPATCHED_CARGO_WEIGHT' (float): Peso da carga despachada em Newton (N).
        - 'CRUISE_ALTITUDE' (float): Altitude de cruzeiro em metros (m).
        - 'CRUISE_VELOCITY' (float): Velocidade de cruzeiro em metros por segundo (m/s).
    ALTITUDE_GLI (float, opcional): Altitude de subida em metros (m). Se None, usa metade da altitude de cruzeiro.
    V_CRUISE (float, opcional): Velocidade de cruzeiro em metros por segundo (m/s). Se None, calcula a partir dos parâmetros de voo.
    plot (bool, opcional): Se True, plota o gráfico da taxa de subida por velocidade. Padrão é False.
    display (bool, opcional): Se True, exibe o gráfico. Padrão é False.

    Retorna:
    dict: Dicionário contendo os resultados:
        - "MAX_GAMMA_CLIMB" (float): Ângulo máximo de subida (adimensional).
        - "MAX_RATE_OF_CLIMB" (float): Taxa máxima de subida em metros por segundo (m/s).
        - "GRAPH_RATE_OF_CLIMB_PER_VELOCITY" (fig): Figura do gráfico da taxa de subida por velocidade, se plot for True.

    A função calcula o ângulo máximo de subida (gamma_max) e a taxa máxima de subida (h_max) usando as equações relevantes
    e os parâmetros fornecidos. Se plot for True, plota e opcionalmente exibe o gráfico da taxa de subida em função da velocidade.
    """

    logger = get_logger(log_name="CLIMB")

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']
    S = aircraft_parameters['S']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)

    W = TOW - 0.10 * FW

    altitude = flight_parameters['CRUISE_ALTITUDE'] / 2 if ALTITUDE_GLI is None else ALTITUDE_GLI
    rho = aero.get_density(altitude=altitude)

    sigma = aero.get_sigma(altitude=altitude)

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    n = (aircraft_parameters['TSFC'] / 3600)

    T_Em_SSL = aero.calculate_general_thrust(thrust_factor=n, altitude=0, sea_level_thrust=T)

    E_m = aircraft_parameters['E_m']

    # # 10.30 - OJHA - Max Gamma (Steepest Climb)
    gamma_max = (T_Em_SSL * sigma / W) - (1 / E_m)

    TT = 1 + math.sqrt(1 + 3/(E_m**2 * (T_Em_SSL * sigma/W)**2))

    h_max = (
            math.sqrt(((W/S)*TT)/(3 * aero.rho_0*CD0)) *
            (T_Em_SSL/W)**1.5 *
            (1 - TT/6) *
            (sigma - 1/(
                (2*TT/3)*(1-TT/6)*(E_m**2)*(T_Em_SSL/W)**2 * sigma
            )))

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, queremos computar o valor
        V_cru = calc_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)[
            'CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE

    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    if plot is True:


        V_linspace = linspace(0.3 * V_cru, 4 * V_cru, 100)
        h_dot_list = []
        for v_i in V_linspace:

            # Gud - 18.18
            q_i = 0.5 * rho * v_i ** 2
            h_dot_i = v_i * (T_Em_SSL * sigma / W - q_i * (S/W)*CD0 - K*(W/S) * 1/q_i)

            h_dot_list.append(h_dot_i)


        filter_h_dot_list = [h for h in h_dot_list if h >= 0]
        filter_V_linspace = [V_linspace[i] for i, v in enumerate(h_dot_list) if v >= 0]

        fig_climb = plt.figure(figsize=(5, 5))
        plt.plot(filter_V_linspace, filter_h_dot_list, c='black')
        plt.xlabel("Velocity [m/s]", size=12)
        plt.ylabel("Rate of Climb [m/s]", size=12)
        plt.title("Rate of Climb per Velocity")
        plt.ylim(0, max(h_dot_list) + 1)
        plt.grid()

        if display is True:
            plt.show()
        else:
            pass

    return {
        "MAX_GAMMA_CLIMB": gamma_max,
        "MAX_RATE_OF_CLIMB": h_max,
        "GRAPH_RATE_OF_CLIMB_PER_VELOCITY": fig_climb if plot is True else None
    }


def calc_distance_time_steepest_climb(aircraft_parameters: dict, flight_parameters: dict):
    """
    Calcula a distância, o tempo e o consumo de combustível para a subida mais íngreme de uma aeronave.

    Parâmetros:
    aircraft_parameters (dict): Dicionário contendo os parâmetros da aeronave.
        - 'OEW' (float): Peso operacional vazio da aeronave em Newtons (N).
        - 'CD0' (float): Coeficiente de arrasto de arrasto zero (adimensional).
        - 'K' (float): Coeficiente de arrasto induzido (adimensional).
        - 'S' (float): Área da asa (m²).
        - 'T0' (float): Empuxo ao nível do mar por motor em Newtons (N).
        - 'NE' (int): Número de motores.
        - 'TSFC' (float): Consumo específico de combustível por empuxo em kg/N.s.
        - 'E_m' (float): Eficiência aerodinâmica máxima (adimensional).
    flight_parameters (dict): Dicionário contendo os parâmetros do voo.
        - 'NUMBER_OF_PASSENGERS' (int): Número de passageiros.
        - 'FUEL_WEIGHT' (float): Peso do combustível em Newtons (N).
        - 'DISPATCHED_CARGO_WEIGHT' (float): Peso da carga despachada em Newtons (N).
        - 'CRUISE_ALTITUDE' (float): Altitude de cruzeiro em metros (m).

    Retorna:
    dict: Dicionário contendo os resultados:
        - "STEEPEST_CLIMB_TIME" (float): Tempo de subida mais íngreme em segundos (s).
        - "STEEPEST_CLIMB_DISTANCE" (float): Distância de subida mais íngreme em metros (m).
        - "STEEPEST_CLIMB_FUEL_CONSUMPTION" (float): Consumo de combustível durante a subida mais íngreme (adimensional).

    A função calcula a distância, o tempo e o consumo de combustível para a subida mais íngreme usando as equações relevantes
    e os parâmetros fornecidos. Utiliza a fórmula de empuxo geral, a razão da densidade do ar e outros parâmetros aerodinâmicos
    para determinar os valores.
    """

    logger = get_logger(log_name="CLIMB")

    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']
    S = aircraft_parameters['S']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)

    W0 = TOW
    W = TOW - 0.10 * FW

    altitude = flight_parameters['CRUISE_ALTITUDE']
    climb_parameters = get_climb_parameters(altitude=altitude)

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    n = (aircraft_parameters['TSFC'] / 3600)

    T_Em_SSL = aero.calculate_general_thrust(thrust_factor=n, altitude=0, sea_level_thrust=T)

    sigma_0 = aero.get_sigma(altitude=0)

    V_Em_SSL = math.sqrt((2 * W/S)/(aero.rho_0 * sigma_0)) * (K/CD0)**0.25  # 10.31

    h1 = aero.h_Sc
    h2 = altitude

    e = climb_parameters['e']
    beta = climb_parameters['beta']
    h_rix = climb_parameters['h_rix']

    E_m = aircraft_parameters['E_m']

    A = math.sqrt(W / W0) * (V_Em_SSL / E_m)  # 10.36
    B = (E_m / (W / W0)) * (T_Em_SSL / W0)    # 10.37

    t1 = (1 * math.sqrt(B * e)) * math.exp(-1 * (h1 - h_rix) / (2 * beta)) - 1
    t2 = (1 * math.sqrt(B * e)) * math.exp(-1 * (h2 - h_rix) / (2 * beta)) + 1
    t3 = (1 * math.sqrt(B * e)) * math.exp(-1 * (h1 - h_rix) / (2 * beta)) + 1
    t4 = (1 * math.sqrt(B * e)) * math.exp(-1 * (h2 - h_rix) / (2 * beta)) - 1

    # 10.46
    t_sc = (
            (beta / (A * math.sqrt(B))) *
            math.log((t1 * t2) / (t3 * t4)))

    x1 = B * e - math.exp((h1 - h_rix) / beta)
    x2 = B * e - math.exp((h2 - h_rix) / beta)

    x_sc = beta * E_m * math.log(x1 / x2)

    climb_parameters_h1 = get_climb_parameters(altitude=h1)
    climb_parameters_h2 = get_climb_parameters(altitude=h2)

    e_1, e_2 = climb_parameters_h1['e'], climb_parameters_h2['e']
    beta_1, beta_2 = climb_parameters_h1['beta'], climb_parameters_h2['beta']
    hrix_1, hrix_2 = climb_parameters_h1['h_rix'], climb_parameters_h2['h_rix']


    sigma_1 = e_1 * math.exp(-(h1-hrix_1)/beta_1)
    sigma_2 = e_2 * math.exp(-(h2-hrix_2)/beta_2)

    #OJHA - 10.52
    zeta_sc = (
            1 -
            math.exp(
                (2*beta*n*(T_Em_SSL/W))/(A*B) *
                ((math.sqrt(sigma_2) - math.sqrt(sigma_1)) +
                 (1/(2*math.sqrt(B))) * math.log(((math.sqrt(B*sigma_2) - 1)*(math.sqrt(B*sigma_2) + 1))/((math.sqrt(B*sigma_1) + 1)*(math.sqrt(B*sigma_1) - 1)))
                 )
            )
    )


    return {
        "STEEPEST_CLIMB_TIME": t_sc,
        "STEEPEST_CLIMB_DISTANCE": x_sc,
        "STEEPEST_CLIMB_FUEL_CONSUPTION": zeta_sc
    }


def calc_service_ceiling(aircraft_parameters: dict, flight_parameters: dict):
    """
    Calcula o teto de serviço, o teto de desempenho e o teto operacional de uma aeronave.

    Parâmetros:
    aircraft_parameters (dict): Dicionário contendo os parâmetros da aeronave.
        - 'OEW' (float): Peso operacional vazio da aeronave em Newtons (N).
        - 'CD0' (float): Coeficiente de arrasto parasita (adimensional).
        - 'K' (float): Coeficiente de arrasto induzido (adimensional).
        - 'S' (float): Área da asa (m²).
        - 'T0' (float): Empuxo ao nível do mar por motor em Newtons (N).
        - 'NE' (int): Número de motores.
        - 'TSFC' (float): Consumo específico de combustível por empuxo em kg/N.s.
        - 'E_m' (float): Eficiência aerodinâmica máxima (adimensional).
    flight_parameters (dict): Dicionário contendo os parâmetros do voo.
        - 'NUMBER_OF_PASSENGERS' (int): Número de passageiros.
        - 'FUEL_WEIGHT' (float): Peso do combustível em Newtons (N).
        - 'DISPATCHED_CARGO_WEIGHT' (float): Peso da carga despachada em Newtons (N).
        - 'CRUISE_ALTITUDE' (float): Altitude de cruzeiro em metros (m).

    Retorna:
    dict: Dicionário contendo os resultados:
        - "SERVICE_CEILING" (float): Teto de serviço em metros (m).
        - "PERFORMANCE_CEILING" (float): Teto de desempenho em metros (m).
        - "OPERATIONAL_CEILING" (float): Teto operacional em metros (m).
        - "RATE_OF_CLIMB_PER_ALTITUDE" (matplotlib.figure.Figure): Gráfico da razão de subida por altitude.

    A função calcula o teto de serviço, o teto de desempenho e o teto operacional usando os parâmetros da aeronave e do voo.
    Utiliza a densidade do ar, o empuxo geral e outros parâmetros aerodinâmicos para determinar os valores de teto.
    """

    altitude = flight_parameters['CRUISE_ALTITUDE']
    altitude_linspace = linspace(0.1*altitude, 3*altitude, 50)

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']
    S = aircraft_parameters['S']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    n = (aircraft_parameters['TSFC'] / 3600)

    E_m = aircraft_parameters['E_m']
    T_Em_SSL = aero.calculate_general_thrust(thrust_factor=n, altitude=0, sea_level_thrust=T)

    W = TOW - 0.10 * FW

    roc_linspace = []

    for altitude_i in altitude_linspace:

        sigma_i = aero.get_sigma(altitude=altitude_i)

        #OJHA - 10.65
        TT_i = 1 + math.sqrt(1 + 3 / (E_m ** 2 * (T_Em_SSL * sigma_i / W) ** 2))

        h_max_i = (
                math.sqrt(((W / S) * TT_i) / (3 * aero.rho_0 * CD0)) *
                (T_Em_SSL / W) ** 1.5 *
                (1 - TT_i / 6) *
                (sigma_i - 1 / (
                        (2 * TT_i / 3) * (1 - TT_i / 6) * (E_m ** 2) * (T_Em_SSL / W) ** 2 * sigma_i
                )))

        roc_linspace.append(h_max_i)

    poly_ceiling = polyfit(roc_linspace, altitude_linspace, deg=3)
    service_ceiling = polyval(poly_ceiling, x=0.51)
    performance_ceiling = polyval(poly_ceiling, x=0.76)
    operational_ceiling = polyval(poly_ceiling, x=2.54)

    fig_ceiling = plt.figure(figsize=(5, 5))
    plt.plot(roc_linspace, [h/1000 for h in altitude_linspace], c='black', label="Rate Of Climb")
    plt.axhline(y=service_ceiling/1000, label=f"Service Ceiling = {round(service_ceiling/1000, 2)}", color='red')
    plt.axhline(y=performance_ceiling/1000, label=f"Performance Ceiling = {round(performance_ceiling/1000, 2)}", color='blue')
    plt.axhline(y=operational_ceiling/1000, label=f"Operational Ceiling= {round(operational_ceiling/1000, 2)}", color='green')
    plt.xlabel("Rate of Climb [m/s]", size=12)
    plt.ylabel("Altitude [km]", size=12)
    plt.title("Rate of Climb per Altitude")
    plt.xlim(-10, max([h/1000 for h in altitude_linspace]))
    plt.grid()
    plt.legend()

    return {
        "SERVICE_CEILING": service_ceiling,
        "PERFORMANCE_CEILING": performance_ceiling,
        "OPERATIONAL_CEILING": operational_ceiling,
        "RATE_OF_CLIMB_PER_ALTITUDE": fig_ceiling
    }


def calc_distance_time_fastest_climb(aircraft_parameters: dict, flight_parameters: dict):
    """
    Calcula o tempo, distância e consumo de combustível para a subida mais rápida da aeronave.

    Parâmetros:
    aircraft_parameters (dict): Dicionário contendo os parâmetros da aeronave.
        - 'OEW' (float): Peso operacional vazio da aeronave em Newtons (N).
        - 'CD0' (float): Coeficiente de arrasto parasita (adimensional).
        - 'K' (float): Coeficiente de arrasto induzido (adimensional).
        - 'S' (float): Área da asa (m²).
        - 'T0' (float): Empuxo ao nível do mar por motor em Newtons (N).
        - 'NE' (int): Número de motores.
        - 'TSFC' (float): Consumo específico de combustível por empuxo em kg/N.s.
        - 'E_m' (float): Eficiência aerodinâmica máxima (adimensional).
    flight_parameters (dict): Dicionário contendo os parâmetros do voo.
        - 'NUMBER_OF_PASSENGERS' (int): Número de passageiros.
        - 'FUEL_WEIGHT' (float): Peso do combustível em Newtons (N).
        - 'DISPATCHED_CARGO_WEIGHT' (float): Peso da carga despachada em Newtons (N).
        - 'CRUISE_ALTITUDE' (float): Altitude de cruzeiro em metros (m).

    Retorna:
    dict: Dicionário contendo os resultados:
        - "FASTEST_CLIMB_TIME" (float): Tempo de subida mais rápida em segundos.
        - "FASTEST_CLIMB_DISTANCE" (float): Distância percorrida durante a subida mais rápida em metros.
        - "FASTEST_CLIMB_FUEL_CONSUPTION" (float): Consumo de combustível durante a subida mais rápida (adimensional).
        - "FASTEST_CLIMB_FUEL_CONSUMED" (float): Quantidade de combustível consumido durante a subida mais rápida em Newtons (N).

    """

    logger = get_logger(log_name="CLIMB")

    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']
    S = aircraft_parameters['S']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']
    TOW = float(NP * aero.person_weight + OEW + FW + CW)

    W = TOW - 0.10 * FW

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    n = (aircraft_parameters['TSFC'] / 3600)

    E_m = aircraft_parameters['E_m']
    T_Em_SSL = aero.calculate_general_thrust(thrust_factor=n, altitude=0, sea_level_thrust=T)

    altitude = flight_parameters['CRUISE_ALTITUDE'] / 2
    sigma = aero.get_sigma(altitude=altitude)
    climb_parameters = get_climb_parameters(altitude=altitude)

    h1 = aero.h_Sc
    h2 = altitude

    e = climb_parameters['e']
    beta = climb_parameters['beta']
    h_rix = climb_parameters['h_rix']


    # OJHA - 10.62
    TT = (1 +
          math.sqrt(1 +
                    3/(E_m**2 * (T_Em_SSL/W)**2 * sigma**2)
                    )
          )

    b = (
            math.sqrt(
                (2*TT/3) * (1 - TT/6)
            ) * (T_Em_SSL/W)*E_m)


    #OHJA - 10.70

    t_fc_1 = math.sqrt((3*aero.rho_0*CD0)/(W*TT/S))

    t_fc_2 = (beta*b)/(2*((T_Em_SSL/W)**1.5)*(1-TT/6))

    t_fc_31 = (b*e*math.exp(-1*(h1-h_rix)/beta) - 1)/(b*e*math.exp(-1*(h1-h_rix)/beta) + 1)
    t_fc_32 = (b*e*math.exp(-1*(h2-h_rix)/beta) + 1)/(b*e*math.exp(-1*(h2-h_rix)/beta) - 1)

    t_fc = t_fc_1 * t_fc_2 * math.log(t_fc_31 * t_fc_32)

    # OHJA - 10.73
    x_fc_1 = (beta*b)/(2*(T_Em_SSL/W)*(1 - TT/6))

    x_fc_21 = (b*e*math.exp(-1*(h1-h_rix)/beta) - 1)*(b*e*math.exp(-1*(h2-h_rix)/beta) + 1)
    x_fc_22 = (b*e*math.exp(-1*(h1-h_rix)/beta) + 1)*(b*e*math.exp(-1*(h2-h_rix)/beta) - 1)

    x_fc = x_fc_1 * math.log(x_fc_21/x_fc_22)

    # OHJA - 10.76
    zeta_fc_1 = math.sqrt(
        (3*aero.rho_0*CD0) /
        ((T_Em_SSL/W)*(W/S)/TT)
    )

    zeta_fc_2 = (beta*n)/(2 * (1-TT/6))

    zeta_fc_31 = (b**2) * (e**2) * math.exp(-2*(h2-h_rix)/beta) - 1
    zeta_fc_32 = (b**2) * (e**2) * math.exp(-2*(h1-h_rix)/beta) - 1

    zeta_fc = 1 - math.exp(zeta_fc_1 * zeta_fc_2 * math.log(zeta_fc_31/zeta_fc_32))

    W_1 = W
    W_2 = W_1 * (1 - zeta_fc)
    delta_fuel = W_1 - W_2
    percent_reduction = delta_fuel / W_1

    return {
        "FASTEST_CLIMB_TIME": t_fc,
        "FASTEST_CLIMB_DISTANCE": x_fc,
        "FASTEST_CLIMB_FUEL_CONSUPTION": zeta_fc,
        "FASTEST_CLIMB_FUEL_CONSUMED": delta_fuel
    }
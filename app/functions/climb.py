import math
from .aero import Aero
from .utils import get_logger, linspace
from functions.cruising_jet import calc_cruise_velocity
import matplotlib.pyplot as plt
from numpy import polyfit, polyval

aero = Aero()


def get_climb_parameters(altitude):

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
    logger.debug(f"rho: {rho}")

    sigma = aero.get_sigma(altitude=altitude)
    logger.debug(f"Sigma: {sigma}")

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    n = (aircraft_parameters['TSFC'] / 3600)

    T_Em_SSL = aero.calculate_general_thrust(thrust_factor=n, altitude=0, sea_level_thrust=T)
    logger.debug(f"calc_max_climb_angle_rate_of_climb| T_Em_SSL: {T_Em_SSL}")
    logger.debug(f"calc_max_climb_angle_rate_of_climb| W: {W}")

    logger.debug(f"calc_max_climb_angle_rate_of_climb| T_Em_SSL/W : {T_Em_SSL / W}")

    E_m = aircraft_parameters['E_m']
    logger.debug(f"E_m: {E_m}")

    # # 10.30 - OJHA - Max Gamma (Steepest Climb)
    gamma_max = (T_Em_SSL * sigma / W) - (1 / E_m)
    logger.debug(f"Max Gamma: {gamma_max}")


    # Gud - 18.25 Max Rate of Climb (Fastest Climb)
    # Z = 1 + math.sqrt(1 + 3/(E_m ** 2 / ((T_Em_SSL * sigma)/W)**2))
    #
    # h_max = ((math.sqrt((W * Z / S)/(3 * rho * CD0)) * (T_Em_SSL * sigma/W)**1.5) *
    #          (1 - Z/6) - (3 * 1)/(2 * (T_Em_SSL * sigma / W) ** 2 * (E_m ** 2) * Z))

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

        logger.debug(f"CRUISE_VELOCITY: {V_cru}")

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
    logger.debug(f"sigma_0: {sigma_0}")

    V_Em_SSL = math.sqrt((2 * W/S)/(aero.rho_0 * sigma_0)) * (K/CD0)**0.25  # 10.31
    logger.debug(f"V_Em_SSL: {V_Em_SSL}")

    h1 = aero.h_Sc
    h2 = altitude

    e = climb_parameters['e']
    beta = climb_parameters['beta']
    h_rix = climb_parameters['h_rix']

    E_m = aircraft_parameters['E_m']
    logger.debug(f"E_m: {E_m}")

    A = math.sqrt(W / W0) * (V_Em_SSL / E_m)  # 10.36
    B = (E_m / (W / W0)) * (T_Em_SSL / W0)    # 10.37

    t1 = (e * math.sqrt(B)) * math.exp(-1 * (h1 - h_rix) / (2 * beta)) - 1
    t2 = (e * math.sqrt(B)) * math.exp(-1 * (h2 - h_rix) / (2 * beta)) + 1
    t3 = (e * math.sqrt(B)) * math.exp(-1 * (h1 - h_rix) / (2 * beta)) + 1
    t4 = (e * math.sqrt(B)) * math.exp(-1 * (h2 - h_rix) / (2 * beta)) - 1

    t_sc = (beta / (A * math.sqrt(B)) * math.log((t1 * t2) / (t3 * t4)))

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

    logger.debug(f"zeta_sc: {zeta_sc}")

    return {
        "STEEPEST_CLIMB_TIME": t_sc,
        "STEEPEST_CLIMB_DISTANCE": x_sc,
        "STEEPEST_CLIMB_FUEL_CONSUPTION": zeta_sc
    }


def calc_service_ceiling(aircraft_parameters: dict, flight_parameters: dict):

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

        rho_i = aero.get_density(altitude=altitude_i)
        sigma_i = aero.get_sigma(altitude=altitude_i)

        # 18.25 Gud Max Rate of Climb (Fastest Climb)
        # Z_i = 1 + math.sqrt(1 + 3 / ((E_m ** 2) / ((T_Em_SSL * sigma_i) / W) ** 2))
        #
        # h_max_i = ((math.sqrt((W * Z_i / S) / (3 * rho_i * CD0)) * (T_Em_SSL * sigma_i / W) ** 1.5) *
        #          (1 - Z_i / 6) - (3 * 1) / (2 * (T_Em_SSL * sigma_i / W) ** 2 * (E_m ** 2) * Z_i))


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
    logger.debug(f"calc_distance_time_fastest_climb | T_Em_SSL: {T_Em_SSL}")
    logger.debug(f"calc_distance_time_fastest_climb | W: {W}")
    logger.debug(f"calc_distance_time_fastest_climb | T_Em_SSL/W: {T_Em_SSL/W}")

    altitude = flight_parameters['CRUISE_ALTITUDE'] / 2
    sigma = aero.get_sigma(altitude=altitude)
    climb_parameters = get_climb_parameters(altitude=altitude)
    logger.debug(f"calc_distance_time_fastest_climb | climb_parameters: {climb_parameters}")

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

    logger.debug(f"calc_distance_time_fastest_climb | TT: {TT}")

    b = (
            math.sqrt(
                (2*TT/3) * (1 - TT/6)
            ) * (T_Em_SSL/W)*E_m)

    logger.debug(f"calc_distance_time_fastest_climb | b: {b}")

    #OHJA - 10.70

    t_fc_1 = math.sqrt((3*aero.rho_0*CD0)/(W*TT/S))

    t_fc_2 = (beta*b)/(2*((T_Em_SSL/W)**1.5)*(1-TT/6))

    t_fc_31 = (b*e*math.exp(-1*(h1-h_rix)/beta) - 1)/(b*e*math.exp(-1*(h1-h_rix)/beta) + 1)
    t_fc_32 = (b*e*math.exp(-1*(h2-h_rix)/beta) + 1)/(b*e*math.exp(-1*(h2-h_rix)/beta) - 1)

    t_fc = t_fc_1 * t_fc_2 * math.log(t_fc_31 * t_fc_32)
    logger.debug(f"calc_distance_time_fastest_climb | t_fc: {t_fc}")

    # OHJA - 10.73
    x_fc_1 = (beta*b)/(2*(T_Em_SSL/W)*(1 - TT/6))

    x_fc_21 = (b*e*math.exp(-1*(h1-h_rix)/beta) - 1)*(b*e*math.exp(-1*(h2-h_rix)/beta) + 1)
    x_fc_22 = (b*e*math.exp(-1*(h1-h_rix)/beta) + 1)*(b*e*math.exp(-1*(h2-h_rix)/beta) - 1)

    x_fc = x_fc_1 * math.log(x_fc_21/x_fc_22)

    logger.debug(f"calc_distance_time_fastest_climb | x_fc_1: {x_fc_1}")
    logger.debug(f"calc_distance_time_fastest_climb | x_fc_21: {x_fc_21}")
    logger.debug(f"calc_distance_time_fastest_climb | x_fc_23: {x_fc_22}")
    logger.debug(f"calc_distance_time_fastest_climb | x_fc: {x_fc/1000}")

    # OHJA - 10.76
    zeta_fc_1 = math.sqrt(
        (3*aero.rho_0*CD0) /
        ((T_Em_SSL/W)*(W/S)/TT)
    )

    zeta_fc_2 = (beta*n)/(2 * (1-TT/6))

    zeta_fc_31 = (b**2) * (e**2) * math.exp(-2*(h2-h_rix)/beta) - 1
    zeta_fc_32 = (b**2) * (e**2) * math.exp(-2*(h1-h_rix)/beta) - 1

    zeta_fc = 1 - math.exp(zeta_fc_1 * zeta_fc_2 * math.log(zeta_fc_31/zeta_fc_32))
    logger.debug(f"calc_distance_time_fastest_climb | zeta_fc: {zeta_fc}")

    W_1 = W
    W_2 = W_1 * (1 - zeta_fc)
    delta_fuel = W_1 - W_2
    percent_reduction = delta_fuel / W_1
    logger.debug(f"calc_distance_time_fastest_climb | delta_fuel: {delta_fuel}")
    logger.debug(f"calc_distance_time_fastest_climb | percent_reduction: {percent_reduction * 1000}")

    return {
        "FASTEST_CLIMB_TIME": t_fc,
        "FASTEST_CLIMB_DISTANCE": x_fc,
        "FASTEST_CLIMB_FUEL_CONSUPTION": zeta_fc,
        "FASTEST_CLIMB_FUEL_CONSUMED": delta_fuel
    }




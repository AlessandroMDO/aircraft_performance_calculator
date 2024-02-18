import math
from .aero import Aero
from .utils import get_logger, linspace
from functions.cruising_jet import calc_cruise_velocity
import matplotlib.pyplot as plt

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


def calc_max_climb_angle_rate_of_climb(aircraft_parameters: dict, flight_parameters: dict, ALTITUDE_GLI=None, V_CRUISE=None,
                         plot=False, display=False):
    logger = get_logger(log_name="CLIMB")

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']
    S = aircraft_parameters['S']

    MTOW = float(NP * aero.person_weight + OEW + FW + CW)

    W = MTOW - 0.02 * FW

    altitude = flight_parameters['CRUISE_ALTITUDE'] / 2 if ALTITUDE_GLI is None else ALTITUDE_GLI
    rho = aero.get_density(altitude=altitude)
    logger.debug(f"rho: {rho}")

    sigma = aero.get_sigma(altitude=altitude)
    logger.debug(f"Sigma: {sigma}")

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    n = aircraft_parameters['TSFC']

    T_Em_SSL = aero.calculate_general_thrust(thrust_factor=n, altitude=0, sea_level_thrust=T)
    logger.debug(f"T_Em_SSL: {T_Em_SSL}")
    logger.debug(f"W: {W}")

    logger.debug(f"T_Em_SSL/W : {T_Em_SSL / W}")

    E_m = 1 / (2 * math.sqrt(K * CD0))
    logger.debug(f"E_m: {E_m}")

    # Max Gamma (Steepest Climb)
    gamma_m = ((T_Em_SSL / W) * sigma) - (1 / E_m)  # 10.30
    logger.debug(f"Max Gamma: {gamma_m}")

    TT = 1 + math.sqrt(1 + 3 / (sigma ** 2 * E_m ** 2 * (T_Em_SSL / W) ** 2))  # 10.62

    # Max Rate of Climb (Fastest Climb) # 10.65
    h_m = (
            math.sqrt((TT * W / S) / (3 * aero.rho_0 * CD0)) *
            ((T_Em_SSL / W) ** 1.5) *
            (1 - TT / 6) *
            (sigma - 1 / (
                    sigma * (2 * TT / 3) * (1 - TT / 6) * (E_m ** 2) * (T_Em_SSL / W) ** 2
            ))
    )

    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        V_cru = calc_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)[
            'CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE

    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    if plot is True:

        logger.debug(f"CRUISE_VELOCITY: {V_cru}")

        V_linspace = linspace(0.3 * V_cru, 4 * V_cru, 40)
        h_dot_list = []
        for v_i in V_linspace:

            E_i = (aero.rho_0 * sigma * (v_i ** 2) * CD0)/(2*W/S) + 2*K*(W/S)/(aero.rho_0 * sigma * v_i ** 2)
            h_dot_i = (((T_Em_SSL * sigma) / W)/v_i) - v_i*E_i

            h_dot_list.append(h_dot_i)

        fig_climb = plt.figure(figsize=(5, 5))
        plt.plot(V_linspace, h_dot_list, c='black')
        plt.xlabel("Velocity [m/s]", size=12)
        plt.ylabel("Rate of Climb [m/s]", size=12)
        plt.title("Rate of climb per velocity")
        plt.grid()
        plt.legend()

        if display is True:
            plt.show()
        else:
            pass

    return {
        "MAX_GAMMA_CLIMB": gamma_m,
        "MAX_RATE_OF_CLIMB": h_m,
        "GRAPH_RATE_OF_CLIMB_PER_VELOCITY": fig_climb if plot is True else None
    }


def calc_distance_time_steepest_climb(aircraft_parameters: dict, flight_parameters: dict):

    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']
    S = aircraft_parameters['S']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    MTOW = float(NP * aero.person_weight + OEW + FW + CW)

    W0 = MTOW
    W = MTOW - 0.02 * FW

    altitude = flight_parameters['CRUISE_ALTITUDE'] / 2
    climb_parameters = get_climb_parameters(altitude=altitude)

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']
    n = aircraft_parameters['TSFC']

    T_Em_SSL = aero.calculate_general_thrust(thrust_factor=n, altitude=0, sea_level_thrust=T)

    # TODO: como calcular estes valores ?

    V_Em_SSL = math.sqrt((2 * W/S)/aero.rho_0) * (K/CD0)**0.25  # 10.31

    h1 = aero.h_Sc
    h2 = altitude

    e = climb_parameters['e']
    beta = climb_parameters['beta']
    h_rix = climb_parameters['h_rix']

    E_m = 1 / (2 * math.sqrt(K * CD0))

    A = (W / W0) ** 0.5 * (V_Em_SSL / E_m)
    B = (E_m / (W / W0)) * (T_Em_SSL / W0)

    t1 = (e * B ** 0.5) * math.exp(-1 * (h1 - h_rix) / (2 * beta)) - 1
    t2 = (e * B ** 0.5) * math.exp(-1 * (h2 - h_rix) / (2 * beta)) + 1
    t3 = (e * B ** 0.5) * math.exp(-1 * (h1 - h_rix) / (2 * beta)) + 1
    t4 = (e * B ** 0.5) * math.exp(-1 * (h2 - h_rix) / (2 * beta)) - 1

    t_sc = (beta / (A * B ** 0.5) * math.log((t1 * t2) / (t3 * t4)))

    x1 = B * e - math.exp((h1 - h_rix) / beta)
    x2 = B * e - math.exp((h2 - h_rix) / beta)

    x_sc = beta * E_m * math.log(x1 / x2)

    return {
        "STEEPEST_CLIMB_TIME": t_sc,
        "STEEPEST_CLIMB_DISTANCE": x_sc
    }


def calc_service_ceiling(aircraft_parameters: dict, flight_parameters: dict):
    pass

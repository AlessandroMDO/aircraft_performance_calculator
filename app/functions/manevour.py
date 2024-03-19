import math
from .aero import Aero
from functions.cruising_jet import calc_cruise_velocity
from numpy import linspace
import matplotlib.pyplot as plt

aero = Aero()


def calc_load_factor_turning_rate_turning_radius_graph(aircraft_parameters: dict, flight_parameters: dict, V_CRUISE=None, display=False,  W_CRUISE=None):

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']

    altitude = flight_parameters['CRUISE_ALTITUDE']
    altitude_linspace = linspace(0.3*altitude, altitude, 3)

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)
    # TOW - (50% do combustível)
    W = TOW - 0.5 * FW if W_CRUISE is None else W_CRUISE

    E_m = 1 / (2 * math.sqrt(K * CD0))

    sigma = aero.get_sigma(altitude=altitude)
    rho_SSL = aero.rho_0

    results_fastest_turn = calc_fastest_turn(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)
    results_tighest_turn = calc_tighest_turn(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)
    results_stall = calc_stall_turn(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)

    VELOCITY_FASTEST_TURN = results_fastest_turn['VELOCITY_FASTEST_TURN']
    LOAD_FACTOR_FASTEST_TURN = results_fastest_turn['LOAD_FACTOR_FASTEST_TURN']
    EFICIENCY_FASTEST_TURN = results_fastest_turn['EFICIENCY_FASTEST_TURN']

    VELOCITY_TIGHEST_TURN = results_tighest_turn['VELOCITY_TIGHEST_TURN']
    LOAD_FACTOR_TIGHEST_TURN = results_tighest_turn['LOAD_FACTOR_TIGHEST_TURN']
    EFICIENCY_TIGHEST_TURN = results_tighest_turn['EFICIENCY_TIGHEST_TURN']

    VELOCITY_STALL = results_stall['VELOCITY_STALL']


    if flight_parameters['CRUISE_VELOCITY'] == 0:
        # Se for zero, quremos computar o valor
        V_cru = calc_cruise_velocity(aircraft_parameters=aircraft_parameters, flight_parameters=flight_parameters)['CRUISE_VELOCITY'] if V_CRUISE is None else V_CRUISE
    else:
        V_cru = flight_parameters['CRUISE_VELOCITY']

    # OJHA - 11.17
    def get_turning_rate(V_i, n_i):

        # OJHA - 11.13
        try:
            phi_i = math.acos(1 / n_i)
        except ValueError as e:
            phi_i = 0

        omega = (aero.g / V_i) * math.tan(phi_i)
        return omega

    # OJHA - 11.18
    def get_radius(V_i, omega_i):
        r_i = V_i / omega_i

        return r_i

    # OJHA - 11.12
    def get_load_factor(V_i):

        try:
            n_i = (((rho_SSL * sigma * CD0 * E_m)/(W/S)) * (V_i ** 2) *
                 math.sqrt(
                     ((2*(T/W)*(W/S))/(CD0*rho_SSL*sigma*V_i**2)) - 1
                 )
                 )
        except ValueError as e:
            n_i = 1

        return n_i

    V_linspace = linspace(0.3 * V_cru, 3.5 * V_cru, 50)

    n_list, omega_list, radius_list = [], [], []

    for V_i in V_linspace:

        n_i = get_load_factor(V_i=V_i)
        omega_i = get_turning_rate(V_i=V_i, n_i=n_i)
        radius_i = get_radius(V_i=V_i, omega_i=omega_i)

        n_list.append(n_i)
        omega_list.append(omega_i)
        radius_list.append(radius_i)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    plt.subplots_adjust(wspace=0.3)  # Adjust the horizontal space between subplots

    # Plot data on the left subplot
    line1, = ax1.plot(V_linspace, n_list, label="Load Factor", color="blue")
    ax1.set_ylabel("Load Factor (n)")
    line3 = ax1.axvline(VELOCITY_FASTEST_TURN, label = f"Fastest Turn Velocity = {round(VELOCITY_FASTEST_TURN, 2)}", color = 'black')
    line4 = ax1.axvline(VELOCITY_TIGHEST_TURN, label = f"Tighest Turn Velocity = {round(VELOCITY_TIGHEST_TURN, 2)}", color = 'black', ls = "--")
    line5 = ax1.axvline(VELOCITY_STALL, label = f"Stall Velocity = {round(VELOCITY_STALL, 2)}", color = 'black', ls = "-.")
    ax1.set_xlabel("Velocity (m/s)")
    ax1.tick_params(axis='y')
    ax1.grid()

    # Create a twin y-axis for Turning Rate (n)
    ax1_right = ax1.twinx()
    line2, = ax1_right.plot(V_linspace, omega_list, label="Turning Rate", color="red")
    ax1_right.set_ylabel("Turning Rate (rad/s)")
    ax1_right.tick_params(axis='y')
    # ax1_right.legend()

    lines = [line1, line2, line3, line4, line5]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels)

    # Plot data on the right subplot
    ax2.plot(V_linspace, [r/1000 for r in radius_list])
    ax2.axvline(VELOCITY_FASTEST_TURN, label = f"Fastest Turn Velocity = {round(VELOCITY_FASTEST_TURN, 2)}", color = 'black')
    ax2.axvline(VELOCITY_TIGHEST_TURN, label = f"Tighest Turn Velocity = {round(VELOCITY_TIGHEST_TURN, 2)}", color = 'black', ls = "--")
    ax2.axvline(VELOCITY_STALL, label = f"Stall Velocity = {round(VELOCITY_STALL, 2)}", color = 'black', ls = "-.")
    ax2.set_ylabel("Turning Radius (km)")
    ax2.set_xlabel("Velocity (m/s)")
    ax2.grid()
    ax2.legend()

    if display is True:
        plt.show()
    else:
        pass

    return fig





def calc_fastest_turn(aircraft_parameters: dict, flight_parameters: dict, V_CRUISE=None, display=False,  W_CRUISE=None):

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']

    altitude = flight_parameters['CRUISE_ALTITUDE']

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']

    sigma = aero.get_sigma(altitude=altitude)
    rho_SSL = aero.rho_0

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)
    # TOW - (50% do combustível)
    W = TOW - 0.5 * FW if W_CRUISE is None else W_CRUISE

    E_m = 1 / (2 * math.sqrt(K * CD0))

    # OJHA - 11.28
    Vft = math.sqrt(2 * (W/S)/(rho_SSL*sigma)) * (K/CD0)**0.25


    # OJHA - 11.29
    nft = math.sqrt(2*(T/W)*E_m - 1)


    Eft = (1 / (T/W)) * math.sqrt(2 * (T/W)*E_m - 1)

    # OJHA - 11.35
    rft = (Vft ** 2)/(aero.g * math.sqrt(nft**2 - 1))

    xft = (aero.g / Vft) * math.sqrt(nft ** 2 - 1)

    return {
        "VELOCITY_FASTEST_TURN": Vft,
        "LOAD_FACTOR_FASTEST_TURN": nft,
        "EFICIENCY_FASTEST_TURN": Eft,
        "RADIUS_FASTEST_TURN": rft,
        "TURNING_RATE_FASTEST_TURN": xft
    }


# OJHA - 11.6
def calc_tighest_turn(aircraft_parameters: dict, flight_parameters: dict, V_CRUISE=None, display=False,  W_CRUISE=None):

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']

    altitude = flight_parameters['CRUISE_ALTITUDE']

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']

    sigma = aero.get_sigma(altitude=altitude)
    rho_SSL = aero.rho_0

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)
    # TOW - (50% do combustível)
    W = TOW - 0.5 * FW if W_CRUISE is None else W_CRUISE

    E_m = 1 / (2 * math.sqrt(K * CD0))

    # OJHA - 11.36
    vtt = (
            2 *
            math.sqrt((K * W / S) / (rho_SSL * sigma * (T/W)))
           )

    ntt = math.sqrt(2 - 1/(E_m**2 * (T/W)**2))

    Ett = ntt / (T / W)

    rtt = (vtt ** 2) / (aero.g * math.sqrt(ntt ** 2 - 1))

    # OJHA - 11.40
    xtt = (aero.g / vtt) * math.sqrt(ntt ** 2 - 1)

    return {
        "VELOCITY_TIGHEST_TURN": vtt,
        "LOAD_FACTOR_TIGHEST_TURN": ntt,
        "EFICIENCY_TIGHEST_TURN": Ett,
        "RADIUS_TIGHEST_TURN": rtt,
        "TURNING_RATE_TIGHEST_TURN": xtt
    }

def calc_stall_turn(aircraft_parameters: dict, flight_parameters: dict, V_CRUISE=None, display=False,  W_CRUISE=None):

    S = aircraft_parameters['S']
    K = aircraft_parameters['K']
    CD0 = aircraft_parameters['CD0']
    CL_max = aircraft_parameters['CL_MAX']

    altitude = flight_parameters['CRUISE_ALTITUDE']

    T0 = aircraft_parameters['T0']
    T = T0 * aircraft_parameters['NE']

    sigma = aero.get_sigma(altitude=altitude)
    rho_SSL = aero.rho_0

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * aero.person_weight + OEW + FW + CW)
    # TOW - (50% do combustível)
    W = TOW - 0.5 * FW if W_CRUISE is None else W_CRUISE

    E_m = 1 / (2 * math.sqrt(K * CD0))

    E_CL_m = CL_max / (CD0 + K * CL_max ** 2)

    vst = math.sqrt((2 * (T/W) * (W/S) * E_CL_m)/(rho_SSL * sigma * CL_max))

    nst = (T/W)*E_CL_m

    xst = (aero.g/vst) * math.sqrt(nst ** 2 - 1)

    rst = (vst ** 2)/(aero.g * math.sqrt(nst ** 2 - 1))

    return {
        "VELOCITY_STALL": vst,
        "LOAD_FACTOR_STALL": nst,
        "EFICIENCY_STALL": E_CL_m,
        "RADIUS_STALL": rst,
        "TURNING_RATE_STALL": xst
    }
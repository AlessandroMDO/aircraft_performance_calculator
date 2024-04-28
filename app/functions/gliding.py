import sys
sys.path.append('functions')
from functions.aero import Aero
from functions.utils import default_graph_colors
from numpy import linspace, arange
import matplotlib.pyplot as plt

import math


c = Aero()
colors = default_graph_colors()

def gliding_angle_rate_of_descent(aircraft_parameters, flight_parameters, altitude=None, W=None, V_gli=None, plot=False, display=False):

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']
    TOW = float(NP * c.person_weight + OEW + FW + CW)

    # TOW - (50% do combustível)
    W = TOW - 0.5 * FW if W is None else W

    CD0 = aircraft_parameters['CD0']
    S = aircraft_parameters['S']
    K = aircraft_parameters['K']

    V_gli = flight_parameters['GLIDING_VELOCITY']

    altitude_cru = flight_parameters['CRUISE_ALTITUDE'] if altitude is None else altitude
    sigma = c.get_sigma(altitude=altitude_cru)
    rho_ssl = c.rho_0

    def get_gliding_angle_rate_of_descent(V_i, sigma):

        part_1 = (rho_ssl * sigma * V_i ** 2 * CD0) / (2 * W / S)
        part_2 = (2 * K * (W / S)) / (rho_ssl * sigma * V_i ** 2)
        gliding_angle = -1 * (part_1 + part_2)
        rate_of_descent = - 1 * V_i * gliding_angle

        return gliding_angle, rate_of_descent

    gliding_angle_cru, rate_of_descent_cru = get_gliding_angle_rate_of_descent(V_i=V_gli, sigma=sigma)

    if plot is True:

        velocity_range = linspace(0.5 * V_gli, 3 * V_gli, 25)
        altitude_values = linspace(0.2 * altitude_cru, altitude_cru, 5)

        fig_rate_of_descent, ax_rate_of_descent = plt.subplots(figsize=(6, 5))
        fig_gliding_angle, ax_gliding_angle = plt.subplots(figsize=(6, 5))

        for altitude_i in altitude_values:

            sigma_i = c.get_sigma(altitude=altitude_i)
            gliding_angle_list = []
            rate_of_descent_list = []

            for V_i in velocity_range:
                gliding_angle_i, rate_of_descent_i = get_gliding_angle_rate_of_descent(V_i=V_i, sigma=sigma_i)
                gliding_angle_list.append(math.degrees(gliding_angle_i))
                rate_of_descent_list.append(-1 * rate_of_descent_i)

            ax_gliding_angle.plot(velocity_range, gliding_angle_list, label=f"Altitude: {altitude_i / 1000:.2f} km")
            ax_rate_of_descent.plot(velocity_range, rate_of_descent_list, label=f"Altitude: {altitude_i / 1000:.2f} km")

        ax_gliding_angle.set_xlabel("Velocity [m/s]", fontsize=14)
        ax_gliding_angle.set_ylabel('Gliding Angle [º]', color="black", fontsize=14)

        ax_rate_of_descent.set_xlabel("Velocity [m/s]", fontsize=14)
        ax_rate_of_descent.set_ylabel('Rate of Descent [m/s]', color="black", fontsize=14)

        ax_rate_of_descent.axvline(V_gli, c=colors['dark_green'], label="Descending Velocity", ls="-.")
        ax_rate_of_descent.legend(loc=0)

        ax_gliding_angle.axvline(V_gli, c=colors['dark_green'], label="Descending Velocity", ls="-.")
        ax_gliding_angle.legend(loc=0)

        ax_gliding_angle.set_title("Gliding angle")
        ax_gliding_angle.grid()

        ax_rate_of_descent.grid()
        ax_rate_of_descent.set_title("Rate of Descent")

        ax_rate_of_descent.yaxis.set_ticks(arange(ax_rate_of_descent.get_ylim()[0], ax_rate_of_descent.get_ylim()[1], 4))
        ax_gliding_angle.yaxis.set_ticks(arange(ax_gliding_angle.get_ylim()[0], ax_gliding_angle.get_ylim()[1], 5))
        plt.tight_layout()
        if display is True:
            plt.show()
        else:
            pass

    result = {
        "GLIDING_ANGLE": round(math.degrees(gliding_angle_cru), 2),
        "GLIDING_RATE_OF_DESCENT": round(rate_of_descent_cru, 2),
        "GLIDING_ANGLE_GRAPH": fig_gliding_angle if plot is True else None,
        "RATE_OF_DESCENT_GRAPH": fig_rate_of_descent if plot is True else None
    }

    return result


def gliding_range_endurance(aircraft_parameters, flight_parameters, W=None, V_gli=None, graph_V=False, graph_CL=False, display=False):

    S = aircraft_parameters['S']
    CL_max = aircraft_parameters['CL_MAX']
    CD0 = aircraft_parameters['CD0']
    K = aircraft_parameters['K']

    NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
    FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
    CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
    OEW = aircraft_parameters['OEW']

    TOW = float(NP * c.person_weight + OEW + FW + CW)

    # TOW - (50% do combustível)
    W = TOW - 0.5 * FW if W is None else W

    beta = 9296

    altitude_final   = 0
    altitude_inicial = flight_parameters['CRUISE_ALTITUDE']

    rho_ssl = c.rho_0

    def gliding_range_endurance_constant_lift():

        CD = c.calculate_general_drag_coefficient(CD0=CD0, K=K, CL=CL_max)
        E_st = CL_max / CD

        def get_x_cl(E_i):
            x_cl = E_i * (altitude_inicial - altitude_final)
            return x_cl

        def get_t_cl(E_i, CL_i):
            # OHJA - 7.24
            t_cl = (2 * beta * E_i * ((rho_ssl * CL_i) / (2 * W / S))**0.5) * (math.e ** (-altitude_final/(2*beta)) - math.e ** (-altitude_inicial/(2*beta)))
            return t_cl

        # Caso padrão (1)
        x_cl_st = get_x_cl(E_i=E_st)
        t_cl_st = get_t_cl(E_i=E_st, CL_i=CL_max)

        # Caso de alcance máximo para CL constante(2)
        CL_max_range_cond = (CD0 / K) ** 0.5
        CD_max_range_cond = (2 * CD0)
        E_max_range = CL_max_range_cond / CD_max_range_cond

        x_cl_max_range = get_x_cl(E_i=E_max_range) # Alcance máximo
        t_cl_max_range = get_t_cl(E_i=E_max_range, CL_i=CL_max_range_cond)  # Autonomia do alcance máximo
        
        # Caso de endurance máximo para CL constante(3)

        CL_max_endurance_cond = math.sqrt(3 * CD0 / K)
        CD_max_endurance_cond = 4 * CD0
        E_max_endurance = CL_max_endurance_cond / CD_max_endurance_cond

        t_cl_max_endurance = get_t_cl(E_i=E_max_endurance, CL_i=CL_max_endurance_cond)  # Autonomia máxima
        x_cl_max_endurance = get_x_cl(E_i=E_max_endurance)  # Alcance máximo da autonomia máxima


        if graph_CL is True:

            CL_i_list = linspace(0.1 * min(CL_max, CL_max_range_cond, CL_max_endurance_cond), 1.2 * max(CL_max, CL_max_range_cond, CL_max_endurance_cond), 20)
            x_cl_i_list, t_cl_i_list = [], []

            for CL_i in CL_i_list:

                CD_i = c.calculate_general_drag_coefficient(CD0=CD0, K=K, CL=CL_i)
                E_i = CL_i / CD_i

                x_cl_i = get_x_cl(E_i=E_i)
                t_cl_i = get_t_cl(E_i=E_i, CL_i=CL_i)

                x_cl_i_list.append(x_cl_i)
                t_cl_i_list.append(t_cl_i)

            fig_cl_constant, ax_cl_constant = plt.subplots(figsize=(6, 5))

            fig1 = ax_cl_constant.plot(CL_i_list, [t/3600 for t in t_cl_i_list], c=colors['blue'], label="Endurance", ls='--')
            ax_cl_constant.set_xlabel("Lit Coefficient [-]", fontsize=14)
            ax_cl_constant.set_ylabel('Time [h]', color="black", fontsize=14)

            fig2 = ax_cl_constant.axvline(CL_max, c=colors['dark_green'], label="CLmax", ls="-.")
            # fig6 = ax_cl_constant.scatter(CL_max_range_cond, t_cl_max_range / 3600, label="Endurance of the maximum range", marker='>', color=colors['green'], s=50)

            fig7 = ax_cl_constant.scatter(CL_max_endurance_cond, t_cl_max_endurance / 3600,
                                          label=f"Maximum Endurance = {round(t_cl_max_endurance / 3600, 2)}", marker='v', color=colors['red'], s=50)

            ax2 = ax_cl_constant.twinx()
            fig3 = ax2.plot(CL_i_list, [x/1000 for x in x_cl_i_list], c='black', label="Range")
            ax2.set_ylabel('Range [km]', color="black", fontsize=14)

            fig4 = ax_cl_constant.scatter(CL_i_list[-1], t_cl_i_list[-1] / 2500, alpha=0)
            fig5 = ax2.scatter(CL_max_range_cond, x_cl_max_range / 1000,
                               label=f"Maximum Range = {round(x_cl_max_range / 1000, 2)}", marker ='<', color=colors['green'], s=50)

            # fig8 = ax2.scatter(CL_max_endurance_cond, x_cl_max_endurance / 1000, label="Range of the maximum endurance", marker='^', color=colors['red'], s = 50)

            lines, labels = ax_cl_constant.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc=0)

            plt.title(f"Range & Endurance per Lift Coefficient\nfrom h2 = {altitude_inicial / 1000} [km] to h1 = {altitude_final / 1000} [km]", fontsize = 12)
            plt.tight_layout()
            ax_cl_constant.grid()

            if display is True:
                plt.show()
            else:
                pass

        result = {
            "GLIDING_RANGE_CONSTANT_LIFT_STANDARD": round(x_cl_st, 2),
            "GLIDING_ENDURANCE_CONSTANT_LIFT_STANDARD": round(t_cl_st, 2),

            "GLIDING_MAX_RANGE_CONSTANT_LIFT": round(x_cl_max_range, 2),
            "GLIDING_ENDURANCE_MAX_RANGE_CONSTANT_LIFT_MAX": round(t_cl_max_range, 2),

            "GLIDING_MAX_ENDURANCE_CONSTANT_LIFT": round(t_cl_max_endurance, 2),
            "GLIDING_RANGE_MAX_ENDURANCE_CONSTANT_LIFT": round(x_cl_max_endurance, 2),

            "GLIDING_RANGE_ENDURANCE_CONSTANT_LIFT_GRAPH": fig_cl_constant if graph_CL is True else None

        }
        return result

    def gliding_range_endurance_constant_airspeed():

        V_gli = flight_parameters['GLIDING_VELOCITY']

        def get_A_B(V_i):

            A = (rho_ssl * CD0 * V_i ** 2) / (2 * W/S)
            B = (2 * K * (W / S)) / (rho_ssl * V_i ** 2)
            return A, B


        def get_x_v(A_i, B_i):

            part_1_range = math.atan((A_i / B_i) * math.e ** (-altitude_final / beta))
            part_2_range = math.atan((A_i / B_i) * math.e ** (-altitude_inicial / beta))

            # 7.19 - OJHA
            x_v = ((beta / B_i) * (part_1_range - part_2_range))

            return x_v

        def get_t_v(V_i):

            part_1_endurance = math.atan((CD0 * rho_ssl ** 2 * (V_i ** 4) * math.e ** (-altitude_final / beta)) / (4 * K * (W/S) ** 2))
            part_2_endurance = math.atan((CD0 * rho_ssl ** 2 * (V_i ** 4) * math.e ** (-altitude_inicial / beta)) / (4 * K * (W/S) ** 2))

            t_v = ((beta * rho_ssl * V_i) / (2 * K * W / S)) * (part_1_endurance - part_2_endurance)

            return t_v

        # Caso padrão (1)
        A_st, B_st = get_A_B(V_i=V_gli)
        x_v_st = get_x_v(A_i=A_st, B_i=B_st)
        t_v_st = get_t_v(V_i=V_gli)

        # Caso máximo alcance (página 200, equação 7.38)
        V_max_range = ((math.sqrt(3) * K) / CD0) ** (1/4) * math.sqrt(2 * (W / S) / rho_ssl) * math.e ** ((altitude_inicial + altitude_final) / (8 * beta))
        A_v_max_range, B_v_max_range = get_A_B(V_i=V_max_range)
        x_v_max_range = get_x_v(A_i=A_v_max_range, B_i=B_v_max_range)
        t_v_max_range = x_v_max_range / V_max_range # Ou get_t_v(CD0_i=CD0, V_i=V_max_range)


        # Caso máxima autonomia (página 205, equação 7.56)
        V_max_endurance = (5/3) ** (1/8) * math.sqrt((2 * W/S) / rho_ssl) * (K/CD0)**(1/4) * math.e ** ((altitude_inicial + altitude_final) / (8*beta))
        A_v_max_endurance, B_v_max_endurance = get_A_B(V_i=V_max_endurance)
        x_v_max_endurance = get_x_v(A_i=A_v_max_endurance, B_i=B_v_max_endurance)
        t_v_max_endurance = x_v_max_endurance / V_max_endurance  # Ou get_t_v(CD0_i=CD0, V_i=V_max_endurance)


        if graph_V is True:
            V_i_list, x_v_i_list, t_v_i_list = [], [], []

            for V_i in linspace(0.1 * min(V_gli, V_max_endurance, V_max_range), 1.2 * max(V_gli, V_max_endurance, V_max_range), 100):

                A_i, B_i = get_A_B(V_i=V_i)
                x_v_i = get_x_v(A_i=A_i, B_i=B_i)
                t_v_i = x_v_i / V_i

                V_i_list.append(V_i)
                x_v_i_list.append(x_v_i)
                t_v_i_list.append(t_v_i)

            fig_v_constant, ax_v_constant = plt.subplots(figsize=(6, 5))

            fig1 = ax_v_constant.plot(V_i_list, [t/3600 for t in t_v_i_list], c=colors['blue'], label="Endurance", ls='--')
            ax_v_constant.set_xlabel("Velocity (m/s)", fontsize=14)
            ax_v_constant.set_ylabel('Time [h]', color="black", fontsize=14)

            fig2 = ax_v_constant.axvline(V_gli, c=colors["dark_green"], label="Gliding Velocity", ls = "-.")
            # fig6 = ax_v_constant.scatter(V_max_range, t_v_max_range / 3600, label="Endurance of the maximum range", marker='<', color=colors['green'],s=50)

            fig7 = ax_v_constant.scatter(V_max_endurance, t_v_max_endurance / 3600,
                                         label=f"Maximum Endurance = {round(t_v_max_endurance / 3600, 2)}", marker='^', color=colors['red'], s=50)

            ax2 = ax_v_constant.twinx()
            fig3 = ax2.plot(V_i_list, [x/1000 for x in x_v_i_list], c='black', label="Range")
            ax2.set_ylabel('Range [km]', color="black", fontsize=14)

            fig4 = ax_v_constant.scatter(V_i_list[-1], t_v_i_list[-1] / 2500, alpha=0)

            fig5 = ax2.scatter(V_max_range, x_v_max_range / 1000,
                               label=f"Maximum Range = {round(x_v_max_range / 1000, 2)}", marker='>', color=colors['green'], s=50)

            # fig8 = ax2.scatter(V_max_endurance, x_v_max_endurance / 1000, label="Range of the maximum endurance", marker='v', color=colors['red'], s=50)

            lines, labels = ax_v_constant.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc=0)

            plt.title(f"Range & Endurance per Velocity \nfrom h2 = {altitude_inicial / 1000} [km] to h1 = {altitude_final / 1000} [km]", fontsize=12)
            ax_v_constant.grid()
            plt.tight_layout()

            if display is True:
                plt.show()
            else:
                pass



        result = {
            "GLIDING_RANGE_CONSTANT_AIRSPEED_STANDARD": round(x_v_st, 2),
            "GLIDING_ENDURANCE_CONSTANT_AIRSPEED_STANDARD": round(t_v_st, 2),

            "GLIDING_MAX_RANGE_CONSTANT_AIRSPEED": round(x_v_max_range, 2),
            "GLIDING_ENDURANCE_MAX_RANGE_CONSTANT_AIRSPEED": round(t_v_max_range, 2),

            "GLIDING_RANGE_MAX_ENDURANCE_CONSTANT_AIRSPEED": round(x_v_max_endurance, 2),
            "GLIDING_MAX_ENDURANCE_CONSTANT_AIRSPEED": round(t_v_max_endurance, 2),

            "GLIDING_RANGE_ENDURANCE_CONSTANT_AIRSPEED_GRAPH": fig_v_constant if graph_V is True else None

        }

        return result

    results_gliding_range_endurance = {
        "GLIDING_CONSTANT_LIFT": gliding_range_endurance_constant_lift(),
        "GLIDING_CONSTANT_AIRSPEED": gliding_range_endurance_constant_airspeed(),
    }

    return results_gliding_range_endurance



from functions.aero import Aero
from functions.utils import *
from functions.cruising_jet import get_cruise_velocity
from numpy import linspace
import matplotlib.pyplot as plt
from functools import lru_cache

c = Aero()


@hash_dict
@lru_cache(maxsize=10)
def gliding_angle(aircraft_parameters, altitude, plot=False):

    CD0 = aircraft_parameters['CD0']
    S = aircraft_parameters['SURFACE_AREA']
    K = aircraft_parameters['K']

    # TODO: qual peso considerar ? MTOW ?
    W = aircraft_parameters['K']

    V_cru = get_cruise_velocity(aircraft_parameters=aircraft_parameters, altitude=altitude, W=W)
    V_cru = 227

    sigma = c.get_sigma(altitude=altitude)
    rho_ssl = c.rho_0

    part_1 = (rho_ssl * sigma * V_cru ** 2 * CD0) / (2 * W / S)
    print(part_1)

    part_2 = (2 * K * (W / S)) / (rho_ssl * sigma * V_cru ** 2)
    print(part_2)

    # gliding_angle_cru = -1 * (
    #                                   (rho_ssl * sigma * V_cru ** 2 * CD0) / (2 * W / S) +
    #                                   (2 * K * (W / S)) / (rho_ssl * sigma * V_cru ** 2))

    gliding_angle_cru = part_1 + part_2

    print(gliding_angle_cru)

    if plot is False:
        return {"gliding_angle_cru": gliding_angle_cru, "V_cru": V_cru}
    else:

        velocity_range = linspace(0.7 * V_cru, 1.3 * V_cru, 25)
        gliding_angle_list = []
        for v_i in velocity_range:
            gliding_i = -1 * (((rho_ssl * sigma * v_i ** 2 * CD0) / (2 * W / S)) + (2 * K * (W / S)) / (rho_ssl * sigma * v_i ** 2))
            gliding_angle_list.append(gliding_i)

        fig_glidding = plt.figure(figsize=(5, 3))
        plt.plot(velocity_range, gliding_angle_list, c='black', label = "Gliding angle")
        plt.axvline(x = V_cru, ymin = 0, ymax = 1, color='r', label = "Cruise Velocity")
        plt.xlabel("Velocity [m/s]", size=12)
        plt.ylabel("Gliding Angle [rad]", size=12)
        plt.title("Gliding angle per gliding velocity")
        plt.grid()
        plt.legend()
        plt.show()

        return {"gliding_angle_cru": gliding_angle_cru, "V_cru": V_cru, "gliding_angle_list": gliding_angle_list, "fig_glidding": fig_glidding}


def rate_of_descent(gliding_results, plot=False):

    gliding_angle_cru = gliding_results["gliding_angle_cru"]
    V_cru = gliding_results["V_cru"]

    rate_of_descent_cru = - 1 * V_cru * gliding_angle_cru

    if plot is False:
        return {"rate_of_descent_cru": rate_of_descent_cru, "V_cru": V_cru}
    else:
        gliding_angle_list = gliding_results["gliding_angle_list"]
        velocity_range = linspace(0.7 * V_cru, 1.3 * V_cru, 25)
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

gliding_results = gliding_angle(aircraft_parameters=aircraft_parameters, altitude=10000, plot=True)
rate_of_descent_results = rate_of_descent(gliding_results=gliding_results, plot = True)


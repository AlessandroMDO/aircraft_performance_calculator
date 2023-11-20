import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import math


class Aero:

    def __init__(self):

        self.R_gas = 287.058  
        self.g = 9.81
        self.rho_0 = self.get_density(altitude=0)
        #self.g = 9.81                       # Aceleração da gravidade [m/s^2]
        self.h_Sc = 15.24                   # Altura mínima de decolagem (screen height)
        #self.R_gas = 287.058                # J/(kg*K) Constante dos gases
        self.maximum_breaking_constant = 0.55 * 9.81
        self.medium_breaking_constant = 0.35 * 9.81
        self.minimum_breaking_constant = 0.15 * 9.81
        self.gamma_Ap = math.radians(3)

    def calculate_general_drag_coefficient(self, S, K, CD0, altitude, V, W):
        rho = self.get_density(altitude=altitude)

        CL = (2 * W) / (S * rho * V ** 2)

        CD = CD0 + K * CL**2

        return CD

    def calculate_general_thrust(self, altitude, thrust_factor, sea_level_thrust):

        T = sea_level_thrust * (self.get_sima(altitude=altitude) ** thrust_factor)
        return T

    def cal(self, p0, t0, a, h0, h1):
        if a != 0:
            t1 = t0 + a * (h1 - h0)
            p1 = p0 * (t1 / t0) ** (-1 * self.g / a / self.R_gas)
        else:
            t1 = t0
            p1 = p0 * math.exp(-self.g / self.R_gas / t0 * (h1 - h0))
        return t1, p1

    #https://gist.github.com/buzzerrookie/5b6438c603eabf13d07e
    def get_density(self, altitude):
        a = [-0.0065, 0, 0.001, 0.0028]
        h = [11000, 20000, 32000, 47000]
        p0 = 101325
        t0 = 288.15
        prevh = 0
        if altitude < 0 or altitude > 47000:
            print("altitude must be in [0, 47000]")
            return
        for i in range(0, 4):
            if altitude <= h[i]:
                temperature, pressure = self.cal(p0, t0, a[i], prevh, altitude)
                break
            else:
                t0, p0 = self.cal(p0, t0, a[i], prevh, h[i])
                prevh = h[i]

        density = pressure / (self.R_gas * temperature)
        return density


    def get_sima(self, altitude):

        rho = self.get_density(altitude=altitude)

        return rho / self.rho_0

    def calculate_stall_velocity(self, W, rho, CL_max, S, logger):

        V_S = math.sqrt(2 * W / (CL_max * S * rho))

        logger.debug(f"Stall Velocity: {V_S}")

        return V_S


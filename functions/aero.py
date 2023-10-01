import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import math



class Constants:
    g = 9.81                                    # Aceleração da gravidade [m/s^2]
    h_Sc = 15.24                                # Altura mínima de decolagem (screen height)
    R_gas = 287.058                             # J/(kg*K) Constante dos gases
    maximum_breaking_constant = 0.55 * 9.81
    medium_breaking_constant = 0.35 * 9.81
    minimum_breaking_constant = 0.15 * 9.81
    # gamma_Ap = np.deg2rad(3)
    gamma_Ap = math.radians(3)


    def calculate_general_drag_coefficient(self, S, K, CD0, altitude, V, W):
        rho = self.get_density(altitude=altitude)

        CL = (2 * W) / (S * rho * V ** 2)

        CD = CD0 + K * CL**2

        return CD

    def calculate_general_thrust(self):
        T = 1
        return T

    def cal(self, p0, t0, a, h0, h1):
        if a != 0:
            t1 = t0 + a * (h1 - h0)
            p1 = p0 * (t1 / t0) ** (-self.g / a / self.R_gas)
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
                # sth like dynamic programming
                t0, p0 = self.cal(p0, t0, a[i], prevh, h[i])
                prevh = h[i]

        density = pressure / (self.R_gas * temperature)
        return density

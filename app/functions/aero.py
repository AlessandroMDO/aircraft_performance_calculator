import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import math
from .utils import get_logger



class Aero:

    def __init__(self):

        self.R_gas = 287.058  
        self.g = 9.81 # Aceleração da gravidade [m/s^2]
        self.rho_0 = self.get_density(altitude=0)
        self.h_Sc = 15.24                   # Altura mínima de decolagem (screen height)
        self.maximum_breaking_constant = 0.55 * 9.81
        self.medium_breaking_constant = 0.35 * 9.81
        self.minimum_breaking_constant = 0.15 * 9.81
        self.gamma_Ap = math.radians(3)
        self.person_weight = 75 * 9.81  # [kg]
        self.logger = get_logger()

    def calculate_general_drag_coefficient(self, K, CD0, S=None, altitude=None, V=None, W=None, CL=None):
        """
            Calcula o coeficiente de arrasto geral com base no coeficiente de sustentação, área da asa, altitude, velocidade, peso e coeficiente de arrasto parasita.

            Parâmetros:
            - K: Coeficiente de inclinação da sustentação (CL por radiano).
            - CD0: Coeficiente de arrasto parasita sem sustentação (CD0).
            - S: Área da asa (opcional, será calculada automaticamente se não fornecida).
            - altitude: Altitude em metros (opcional).
            - V: Velocidade em metros por segundo (opcional).
            - W: Peso da aeronave em Newtons (opcional).
            - CL: Coeficiente de sustentação (opcional, será calculado automaticamente se não fornecido).

            Retorna:
            - CD: Coeficiente de arrasto geral.
            """

        if CL is None:
            rho = self.get_density(altitude=altitude)
            CL = (2 * W) / (S * rho * V ** 2)

        CD = CD0 + K * CL ** 2

        return CD

    def calculate_general_thrust(self, altitude, thrust_factor, sea_level_thrust):

        T = sea_level_thrust * (self.get_sigma(altitude=altitude) ** thrust_factor)
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
    def get_density(self, altitude, get_temp=None):
        a = [-0.0065, 0, 0.001, 0.0028]
        h = [11000, 20000, 32000, 47000]
        p0 = 101325
        t0 = 288.15
        prevh = 0
        if altitude < 0 or altitude > 47000:
            self.logger.error("altitude must be in [0, 47000]")
            return
        for i in range(0, 4):
            if altitude <= h[i]:
                temperature, pressure = self.cal(p0, t0, a[i], prevh, altitude)
                break
            else:
                t0, p0 = self.cal(p0, t0, a[i], prevh, h[i])
                prevh = h[i]

        density = pressure / (self.R_gas * temperature)

        if get_temp is None:
            return density
        else:
            return density, temperature


    def get_sigma(self, altitude: float) -> float:

        """
        Calcula a razão de densidade do ar não-dimensional (sigma) em uma dada altitude.

        Parâmetros:
        - altitude (float): Altitude em metros.

        Retorna:
        float: Razão de densidade do ar não-dimensional (sigma).
        """

        try:
            rho = self.get_density(altitude=altitude)
            sigma = float(rho / self.rho_0)
            return sigma
        except TypeError as error:
            self.logger.error("Error while getting sigma value.")



    def calculate_stall_velocity(self, W, rho, CL_max, S):

        """
        Calculates the stall velocity of an aircraft.

        Parameters:
        - W (float): Aircraft weight in Newtons.
        - rho (float): Air density in kg/m^3.
        - CL_max (float): Maximum coefficient of lift.
        - S (float): Wing reference area in square meters.

        Returns:
        float: Stall velocity in meters per second.
        """

        V_S = math.sqrt(2 * W / (CL_max * S * rho))

        return V_S

    @staticmethod
    def get_haversine_distace(departure, arrival):

        latitude_1 = departure['LATITUDE']
        longitude_1 = departure['LONGITUDE']

        latitude_2 = arrival['LATITUDE']
        longitude_2 = arrival['LONGITUDE']

        lat1, lon1, lat2, lon2 = map(math.radians, [latitude_1, longitude_1, latitude_2, longitude_2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        radius_of_earth = 6_371_000  # Radius of Earth in meters
        distance = radius_of_earth * c
        return distance


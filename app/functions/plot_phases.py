import matplotlib.pyplot as plt
import matplotlib
import random

from .aero import Aero

aero = Aero()

def plot_phases(flight_parameters, results_takeoff_time, results_climb_time, results_cruise_time,
                results_descending_time, results_landing_time):

    #Takeoff

    initial_altitude_takeoff = flight_parameters['takeoff_parameters']['ALTITUDE_TAKEOFF']
    final_altitude_takeoff = initial_altitude_takeoff + aero.h_Sc

    result_takeoff_ground_time = results_takeoff_time['TAKEOFF_GROUND_TIME']
    result_takeoff_rotation_time = results_takeoff_time['TAKEOFF_ROTATION_TIME']
    result_takeoff_transition_time = results_takeoff_time['TAKEOFF_TRANSITION_TIME']
    result_takeoff_climb_time = results_takeoff_time['TAKEOFF_CLIMB_TIME']

    #Climb
    initial_climb_altitude = final_altitude_takeoff
    final_climb_altitude   = flight_parameters['CRUISE_ALTITUDE']

    climb_time = results_climb_time['FASTEST_CLIMB_TIME']

    #Cruise
    final_cruise_altitude = flight_parameters['CRUISE_ALTITUDE']
    fuel = results_cruise_time['DELTA_FUEL']
    valid_fuel = results_cruise_time['VALID_FUEL']


    departure_coods= {
        "LATITUDE": flight_parameters['takeoff_parameters']['LATITUDE_TAKEOFF'],
        "LONGITUDE": flight_parameters['takeoff_parameters']['LONGITUDE_TAKEOFF']
    }

    arrival_cords = {
        "LATITUDE": flight_parameters['landing_parameters']['LATITUDE_LANDING'],
        "LONGITUDE": flight_parameters['landing_parameters']['LONGITUDE_LANDING']
    }

    covered_distance_cruise = aero.get_haversine_distace(departure=departure_coods, arrival=arrival_cords)
    print(f"covered_distance_cruise: {covered_distance_cruise/1000}")

    cruise_velocity = results_cruise_time['RESULT_CRUISE_VELOCITY']['CRUISE_VELOCITY']

    total_cruise_time = covered_distance_cruise/cruise_velocity

    #Descending

    #TODO: Para um voo normal, o ângulo de descida é de aproximadamente 3 graus. Deveria forçar ele aqui ?!
    initial_descending_altitude = final_cruise_altitude
    final_descending_altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING'] + aero.h_Sc
    total_descending_time = results_descending_time['RESULT_DESCENDING_TIME']

    #Landing

    final_landing_altitude = flight_parameters['landing_parameters']['ALTITUDE_LANDING']
    initial_landing_altitude = final_descending_altitude

    result_landing_approach_time = results_landing_time['LANDING_APPROACH_TIME']
    result_landing_flare_time = results_landing_time['LANDING_FLARE_TIME']
    result_landing_rotation_time = results_landing_time['LANDING_ROTATION_TIME']
    result_landing_roll_time     = results_landing_time['LANDING_ROLL_TIME']


    ###########################
    i_time = [
        #Takeoff
        0,
        result_takeoff_ground_time,
        result_takeoff_rotation_time,
        result_takeoff_transition_time,
        result_takeoff_climb_time,

        #Climb
        climb_time,

        # Cruise
        total_cruise_time,

        # Descending
        total_descending_time,

        #Landing

        result_landing_approach_time,
        result_landing_flare_time,
        result_landing_rotation_time,
        result_landing_roll_time


    ]

    i_altitude = [
        #Takeoff
        initial_altitude_takeoff,
        initial_altitude_takeoff,
        initial_altitude_takeoff,
        initial_altitude_takeoff + aero.h_Sc/2,
        final_altitude_takeoff,

        #Climb
        final_climb_altitude,

        #Cruise
        final_cruise_altitude,

        #Descending
        final_descending_altitude,

        #Landing
        final_landing_altitude + aero.h_Sc,
        final_landing_altitude + aero.h_Sc/2,
        final_landing_altitude,
        final_landing_altitude


    ]

    cont_time = [sum(i_time[:i+1])/3600 for i in range(len(i_time))]
    print(f"cont_time: {cont_time}")

    fig, axes = plt.subplots(figsize=(7.5, 1.8))

    axes.plot(cont_time, [altitude/1000 for altitude in i_altitude], marker='o', linestyle='-')
    axes.set_xlabel('Time (h)')
    axes.set_ylabel('Altitude (km)')
    axes.set_title('Altitude vs Time')
    axes.set_xscale('log')

    plt.text(0.5, 0.5, f'Estimated Total Flight Time [h]: {round(cont_time[-1], 2)}',
             fontsize=10, fontfamily='Georgia', color='k',
             ha='left', va='bottom',
             transform=plt.gca().transAxes)

    fuel_color = 'r' if valid_fuel is True else 'k'

    plt.text(0.5, 0.6, f'Necessary Fuel [ton]: {round(fuel, 2)}',
             fontsize=10, fontfamily='Georgia', color=fuel_color,
             ha='left', va='bottom',
             transform=plt.gca().transAxes)

    plt.text(0.5, 0.7, f'Cruise Distance [km]: {round(covered_distance_cruise/1000, 2)}',
             fontsize=10, fontfamily='Georgia', color='k',
             ha='left', va='bottom',
             transform=plt.gca().transAxes)

    plt.grid()

    return fig




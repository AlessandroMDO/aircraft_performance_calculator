import matplotlib.pyplot as plt
# from aero import Aero


# aero = Aero()


#TODO: ajustar este gráfico
def create_route_graph(results):

    cruise_results = results['CRUISE']

    cruise_altitude = cruise_results['CRUISE_ALTITUDE']


    # TAKEOF
    takeoff_results = results['TAKEOFF']
    takeoff_altitude = takeoff_results['TAKEOFF_ALTITUDE']
    total_takeof_time = takeoff_results['TAKEOFF_TIME']

    x_takeof_time = [0, total_takeof_time]
    y_takeoff_altitude = [takeoff_altitude, takeoff_altitude + 15]

    # CLIMB
    climb_results = results['CLIMB']
    rate_of_climb = climb_results['RATE_0F_CLIMB']

    total_climb_time = ((cruise_altitude - (takeoff_altitude + 15))/rate_of_climb) + total_takeof_time
    x_climb_time = [total_takeof_time, total_climb_time]
    y_climb_altitude = [takeoff_altitude + 15, cruise_altitude]

    #CRUISE

    total_cruise_time = total_climb_time + cruise_results['CRUISE_TIME']
    x_cruise_time = [total_climb_time, total_cruise_time]
    y_cruise_altitude = [cruise_altitude, cruise_altitude]



    # cruise_results = results['CRUISE']
    # landing_results = results['LANDING']

    fig_cruzeiro = plt.figure(figsize=(5, 3))
    plt.plot(x_takeof_time, y_takeoff_altitude, color='blue')
    plt.plot(x_climb_time, y_climb_altitude, color='red')
    plt.plot(x_cruise_time, y_cruise_altitude, color='green')

    plt.ylim(0, plt.ylim()[1])
    # plt.xscale('log')
    plt.show()



results = {
    "TAKEOFF": {
        "TAKEOFF_ALTITUDE": 10,
        "TAKEOFF_TIME": 300
    },
    "CLIMB": {
        "MAX_RATE_OF_CLIMB": 10
    },
    "CRUISE": {
        "CRUISE_ALTITUDE": 9000,
        "CRUISE_TIME": 7200
    }
}

create_route_graph(results=results)

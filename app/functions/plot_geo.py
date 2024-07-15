import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from .aero import Aero


aero = Aero()


def get_map(latitude_takeoff=None, longitude_takeoff=None, latitude_landing=None,
             longitude_landing=None, airport_takeoff=None, airport_landing=None):

    """
    Gera um mapa mostrando a rota entre dois pontos geográficos e informações sobre a distância.

    Parâmetros:
    - latitude_takeoff (float): Latitude do ponto de decolagem.
    - longitude_takeoff (float): Longitude do ponto de decolagem.
    - latitude_landing (float): Latitude do ponto de pouso.
    - longitude_landing (float): Longitude do ponto de pouso.
    - airport_takeoff (str): Nome do aeroporto de decolagem.
    - airport_landing (str): Nome do aeroporto de pouso.

    Retorna:
    - fig: Objeto figura do matplotlib contendo o mapa gerado.

    """

    fig, ax = plt.subplots()

    margin = 10
    min_lat = min(latitude_takeoff, latitude_landing) - margin
    max_lat = max(latitude_takeoff, latitude_landing) + margin
    min_lon = min(longitude_takeoff, longitude_landing) - margin
    max_lon = max(longitude_takeoff, longitude_landing) + margin

    map =Basemap(projection='cyl', llcrnrlat=min_lat, urcrnrlat=max_lat, llcrnrlon=min_lon, urcrnrlon=max_lon,lat_ts=20,resolution='c')

    map.drawmapboundary(fill_color='aqua')
    map.fillcontinents(color='coral', lake_color='aqua')

    map.drawcoastlines()
    map.drawcountries()
    map.drawstates()

    map.drawgreatcircle(longitude_takeoff, latitude_takeoff, longitude_landing, latitude_landing, color='b')

    departure = {
        "LATITUDE": latitude_takeoff,
        "LONGITUDE": longitude_takeoff,
    }
    
    arrival = {
        "LATITUDE": latitude_landing,
        "LONGITUDE": longitude_landing,
    }

    great_circule_distance = round(aero.get_haversine_distance(departure, arrival) / 1000, 2)

    plt.title(f'Route from \n{airport_takeoff} to \n{airport_landing}\n Distance: {great_circule_distance} km')
    return fig

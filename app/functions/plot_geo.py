import geopandas as gpd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import contextily as ctx


def get_map(latitude_takeoff, longitude_takeoff, latitude_landing, longitude_landing, airport_takeoff, airport_landing):

    latitude_A = latitude_takeoff
    longitude_A = longitude_takeoff

    latitude_B = latitude_landing
    longitude_B = longitude_landing

    geometry = [Point(longitude_A, latitude_A), Point(longitude_B, latitude_B)]
    gdf_points = gpd.GeoDataFrame(geometry=geometry, crs='EPSG:4326')

    line = LineString([gdf_points.geometry.iloc[0], gdf_points.geometry.iloc[1]])
    gdf_line = gpd.GeoDataFrame(geometry=[line], crs='EPSG:4326')

    fig, ax = plt.subplots()

    gdf_line.plot(ax=ax, color='blue', linewidth=2)
    gdf_points.plot(ax=ax, color='black', markersize=50)
    ctx.add_basemap(ax, crs=gdf_points.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Route from \n{airport_takeoff} to \n{airport_landing}')

    # Display the plot
    plt.legend()
    return fig


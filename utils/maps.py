import geopandas as gpd
from shapely.geometry import Point

def create_geodataframe(data):
    geometry = [Point(xy) for xy in zip(data["LONGITUDE"], data["LATITUDE"])]
    gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")
    return gdf

def plot_crime_map(data):
    gdf = create_geodataframe(data)
    return gdf  # O Streamlit suporta GeoDataFrames diretamente com `st.map`

def plot_heatmap(data):
    gdf = create_geodataframe(data)
    return gdf  # Para heatmaps mais avançados, use Folium

def plot_route_map(data):
    gdf = create_geodataframe(data)
    return gdf  # Implementar lógica adicional se necessário

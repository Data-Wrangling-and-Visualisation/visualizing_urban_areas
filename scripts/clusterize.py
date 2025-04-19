"""
Script for clustering Points of Interest (POIs) in urban areas using various clustering algorithms.
The script processes POI data, applies clustering based on categories, and generates concave hulls
for visualization and analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import yaml
from math import radians, cos, sin, asin, sqrt
from sklearn.cluster import KMeans, OPTICS, SpectralClustering, AffinityPropagation, HDBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from alphashape import alphashape
import pyarrow as pa
import pyarrow.parquet as pq
from typing import Dict, List, Tuple, Any, Union
import numpy.typing as npt
import os
import contextily as ctx
import geopandas as gpd
from shapely.geometry import Point, Polygon
import folium
from folium.plugins import MarkerCluster
import matplotlib.colors as mcolors

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open('./configs/clustering.yaml') as f:
        return yaml.safe_load(f)

def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth.
    
    Args:
        lon1, lat1: Longitude and latitude of first point
        lon2, lat2: Longitude and latitude of second point
        
    Returns:
        Distance in kilometers
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

def calculate_area_metrics(lat_min: float, lat_max: float, long_min: float, long_max: float, 
                         center_lat: float, center_long: float) -> Tuple[float, float, float]:
    """
    Calculate area metrics for the region of interest.
    
    Args:
        lat_min, lat_max: Latitude bounds
        long_min, long_max: Longitude bounds
        center_lat, center_long: Center coordinates
        
    Returns:
        Tuple of (width_km, height_km, area_km2)
    """
    width_km = haversine_distance(long_min, center_lat, long_max, center_lat)
    height_km = haversine_distance(center_long, lat_min, center_long, lat_max)
    area_km2 = width_km * height_km
    return width_km, height_km, area_km2

def create_clustering_model(method: str, params: Dict[str, Any]) -> Any:
    """
    Create a clustering model based on specified method and parameters.
    
    Args:
        method: Clustering algorithm name
        params: Parameters for the clustering algorithm
        
    Returns:
        Initialized clustering model
    """
    models = {
        'kmeans': KMeans,
        'optics': OPTICS,
        'hdbscan': HDBSCAN,
        'spectral': SpectralClustering,
        'gmm': GaussianMixture,
        'affinity': AffinityPropagation
    }
    return models[method](**params)

def calculate_cluster_metrics(X: npt.NDArray[np.float64], labels: npt.NDArray[np.int64]) -> Dict[str, float]:
    """
    Calculate various metrics to evaluate clustering quality.
    
    Args:
        X: Input data points
        labels: Cluster labels
        
    Returns:
        Dictionary of metric names and values
    """
    if len(np.unique(labels)) == 1:
        return {}
        
    return {
        'silhouette': silhouette_score(X, labels),
        'calinski_harabasz': calinski_harabasz_score(X, labels),
        'davies_bouldin': davies_bouldin_score(X, labels)
    }

def create_concave_hull(points: npt.NDArray[np.float64], alpha: float = 0.5) -> Union[npt.NDArray[np.float64], None]:
    """
    Create a concave hull around a set of points.
    
    Args:
        points: Array of points to create hull around
        alpha: Alpha parameter for alphashape (smaller = more concave)
        
    Returns:
        Array of hull coordinates or None if hull creation fails
    """
    try:
        concave_hull = alphashape(points, alpha)
        return np.array(concave_hull.exterior.coords)
    except AttributeError:
        print("Failed to create concave hull - possibly too few points")
        return None

def save_clusters_to_parquet(clusters_info: Dict[str, Dict[int, npt.NDArray[np.float64]]], 
                           output_path: str = './data/processed/clusters.zstd') -> None:
    """
    Save cluster information to a parquet file.
    
    Args:
        clusters_info: Dictionary containing cluster information
        output_path: Path to save the parquet file
    """
    # Prepare flattened data
    data = []
    for group_name, clusters in clusters_info.items():
        for cluster_num, coords in clusters.items():
            data.append({
                'group': group_name,
                'cluster_number': cluster_num,
                'coordinates': coords.tolist()
            })

    # Define schema
    schema = pa.schema([
        ('group', pa.string()),
        ('cluster_number', pa.int64()),
        ('coordinates', pa.list_(pa.list_(pa.float64())))
    ])

    table = pa.Table.from_pylist(data, schema=schema)
    pq.write_table(
        table,
        output_path,
        compression='zstd',
        compression_level=3
    )

def create_geodataframe(points: npt.NDArray[np.float64], labels: npt.NDArray[np.int64]) -> gpd.GeoDataFrame:
    """
    Create a GeoDataFrame from points and their cluster labels.
    
    Args:
        points: Array of points (latitude, longitude)
        labels: Array of cluster labels
        
    Returns:
        GeoDataFrame with points and cluster information
    """
    geometry = [Point(xy) for xy in points]
    gdf = gpd.GeoDataFrame(geometry=geometry)
    gdf['cluster'] = labels
    gdf.crs = "EPSG:4326"  # WGS84
    return gdf

def plot_clusters_on_map(gdf: gpd.GeoDataFrame, category: str, 
                        plot_config: Dict[str, Any], output_dir: str, city: str) -> None:
    """
    Create and save a map visualization of the clusters.
    
    Args:
        gdf: GeoDataFrame containing points and cluster information
        category: Name of the category being plotted
        plot_config: Plotting configuration from YAML
        output_dir: Base directory to save the plot
        city: Name of the city being analyzed
    """
    # Create city-specific output directory
    city_output_dir = os.path.join(output_dir, city)
    os.makedirs(city_output_dir, exist_ok=True)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Plot points with cluster colors
    for cluster in gdf['cluster'].unique():
        cluster_points = gdf[gdf['cluster'] == cluster]
        color = plot_config['cluster_colors'][cluster % len(plot_config['cluster_colors'])]
        cluster_points.plot(ax=ax, color=color, markersize=plot_config['point_size'],
                          label=f'Cluster {cluster}')
    
    try:
        # Try to add basemap using contextily
        import contextily as ctx
        
        # Calculate appropriate zoom level based on the extent
        bounds = gdf.total_bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        # Calculate zoom level based on the larger dimension
        zoom = min(20, max(0, int(round(np.log2(360 / max(width, height))))))
        
        # Add basemap with explicit zoom level
        ctx.add_basemap(
            ax,
            source=ctx.providers.CartoDB.Positron,
            zoom=zoom,
            crs=gdf.crs
        )
    except (ImportError, Exception) as e:
        print(f"Warning: Could not add basemap ({str(e)}). Using simple plot without basemap.")
        # Add grid and labels for better readability
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
    
    # Customize plot
    ax.set_title(f'{city} - {category} Clusters', fontsize=14)
    if plot_config['show_legend']:
        ax.legend()
    
    # Save plot
    if plot_config['save_plots']:
        output_path = os.path.join(city_output_dir, f'{category}_clusters.{plot_config["plot_format"]}')
        plt.savefig(output_path, dpi=plot_config['dpi'], bbox_inches='tight')
    
    if plot_config['show_plots']:
        plt.show()
    else:
        plt.close()

def create_interactive_map(gdf: gpd.GeoDataFrame, category: str, 
                         plot_config: Dict[str, Any], output_dir: str, city: str) -> None:
    """
    Create an interactive Folium map with the clusters.
    
    Args:
        gdf: GeoDataFrame containing points and cluster information
        category: Name of the category being plotted
        plot_config: Plotting configuration from YAML
        output_dir: Base directory to save the map
        city: Name of the city being analyzed
    """
    # Create city-specific output directory
    city_output_dir = os.path.join(output_dir, city)
    os.makedirs(city_output_dir, exist_ok=True)
    
    # Create base map
    center_lat = gdf.geometry.y.mean()
    center_lon = gdf.geometry.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    
    # Add marker clusters
    for cluster in gdf['cluster'].unique():
        cluster_points = gdf[gdf['cluster'] == cluster]
        color = plot_config['cluster_colors'][cluster % len(plot_config['cluster_colors'])]
        
        # Create marker cluster for each cluster
        marker_cluster = MarkerCluster(name=f'Cluster {cluster}').add_to(m)
        
        # Add points to marker cluster
        for idx, row in cluster_points.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=plot_config['point_size'],
                color=color,
                fill=True,
                popup=f'Cluster {cluster}'
            ).add_to(marker_cluster)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    if plot_config['save_plots']:
        output_path = os.path.join(city_output_dir, f'{category}_clusters.html')
        m.save(output_path)

def main():
    # Load configuration
    config = load_config()
    general_parameters = config['general_parameters']
    plot_config = config.get('plotting', {})
    
    # Load and prepare data
    city = general_parameters.get('city')
    df = pd.read_parquet(f'./data/collected/{city}_pois.zstd')
    print(f"Loaded {df.shape[0]} POIs for {city}")
    
    # Extract coordinates and categories
    X = np.array(df[['Latitude', 'Longitude']])
    y = df['Custom'].apply(lambda x: x[0])
    
    # Get unique categories and their data points
    categories = np.unique(y)
    X_by_category = [X[y == cat] for cat in categories]
    
    # Define area of interest
    search_long = general_parameters.get('longitude')
    search_lat = general_parameters.get('latitude')
    half_diagonal = general_parameters.get('half_diagonal_coor')
    
    lat_min = search_lat - half_diagonal
    lat_max = search_lat + half_diagonal
    long_min = search_long - half_diagonal
    long_max = search_long + half_diagonal
    
    # Calculate and print area metrics
    width_km, height_km, area_km2 = calculate_area_metrics(
        lat_min, lat_max, long_min, long_max, search_lat, search_long
    )
    print(f"Analysis area: {area_km2:.2f} km² ({width_km:.2f} km × {height_km:.2f} km)")
    
    # Process each category
    clusters_info = {}
    for category, X_cat in zip(categories, X_by_category):
        technique = config['clustering_techniques'].get(category)
        print(f"\nProcessing category: {category} using {technique['method']}")
        
        # Filter points within area of interest
        mask = ((X_cat[:,0] >= lat_min) & (X_cat[:,0] <= lat_max) & 
                (X_cat[:,1] >= long_min) & (X_cat[:,1] <= long_max))
        X_cat_subset = X_cat[mask]
        
        if len(X_cat_subset) < 10:
            print(f"Skipping {category} - too few points ({len(X_cat_subset)})")
            continue
        
        # Apply clustering
        model = create_clustering_model(technique['method'], technique['params'])
        labels = model.fit_predict(X_cat_subset)
        
        # Calculate and print metrics
        metrics = calculate_cluster_metrics(X_cat_subset, labels)
        if metrics:
            print("\nClustering metrics:")
            for metric, value in metrics.items():
                print(f"{metric}: {value:.2f}")
        
        # Create concave hulls for each cluster
        cluster_info = {}
        for label in np.unique(labels):
            cluster_points = X_cat_subset[labels == label]
            hull = create_concave_hull(cluster_points)
            if hull is not None:
                cluster_info[label] = hull
                print(f"Cluster {label}: Reduced to {len(hull)/len(cluster_points):.1%} of points")
        
        clusters_info[category] = cluster_info
        
        # Plot clusters if enabled
        if plot_config.get('enabled', False):
            gdf = create_geodataframe(X_cat_subset, labels)
            plot_clusters_on_map(gdf, category, plot_config, plot_config['output_dir'], city)
            create_interactive_map(gdf, category, plot_config, plot_config['output_dir'], city)
    
    # Save results
    save_clusters_to_parquet(clusters_info)
    print("\nClustering results saved to parquet file")

if __name__ == "__main__":
    main()
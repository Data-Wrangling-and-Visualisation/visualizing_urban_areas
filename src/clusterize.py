import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import yaml
from math import radians, cos, sin, asin, sqrt
from sklearn.cluster import KMeans, OPTICS,SpectralClustering,AffinityPropagation,HDBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
# from shapely.geometry import LineString
from alphashape import alphashape

with open('./src/clustering.yaml') as f:
    config = yaml.safe_load(f)
general_parameters=config['general_parameters']

# Load data
city=general_parameters.get('city')
df = pd.read_parquet(f'./data/collected/{city}_pois.zstd')
print(df.head)
X = np.array(df[['Latitude', 'Longitude']])
# Reduces classes to 1 for each poi
y = df['Custom'].map(lambda x: x[2:-2].replace('"','').split(',')[0])

# Dont use since haversine distance 
# scaler=StandardScaler()
# X=scaler.fit_transform(X)

classes = np.unique(y)
X_class=[]
n_classes = len(classes)

# Each class number of data points
for cls in classes:
    X_cls = X[y == cls]
    X_class.append(X_cls)
    print(X_cls.shape)

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

# choose area
# Take subset of neighbouring data
print('longitude range:',X[:,0].min(),X[:,0].max())
print('latitude range: ',X[:,1].min(),X[:,1].max())
print('max half_diag_coor: ',X[:,1].max()-X[:,1].min())
search_long=general_parameters.get('longitude')
search_lat=general_parameters.get('latitude')
random_half_diagonal=general_parameters.get('half_diagonal_coor')

# take center+-random_half_diagonal subset
lat_min = search_lat - random_half_diagonal
lat_max = search_lat + random_half_diagonal
long_min = search_long - random_half_diagonal
long_max = search_long + random_half_diagonal

# Area in km^2
width_km = haversine(long_min, search_lat, long_max, search_lat)
height_km = haversine(search_long, lat_min, search_long, lat_max)
area_km2 = width_km * height_km
print(f'Area km^2={area_km2}')
print("Algorithm parameters:")

clusters_info={} # cls: [cluster_number:cluster_info, ...]
# cls is one of [Nature, Tourist, Elite r.e., ...]
# see below cluster_info structure
for idx, (X_cls, cls) in enumerate(zip(X_class, classes)):
    technique = config['clustering_techniques'].get(cls)
    print(cls,technique)
    
    # Take subset of values from current class
    mask = ((X_cls[:,0] >= lat_min) & (X_cls[:,0] <= lat_max) & 
            (X_cls[:,1] >= long_min) & (X_cls[:,1] <= long_max))
    
    X_cls_subset = X_cls[mask]
    
    if len(X_cls_subset) < 10:
        continue
    
    # Apply clustering. label is numeric cluster name
    if technique['method'] == 'kmeans':
        model = KMeans(**technique['params']).fit(X_cls_subset)
        labels = model.labels_
    elif technique['method'] == 'optics':
        model = OPTICS(**technique['params']).fit(X_cls_subset)
        labels = model.labels_
    elif technique['method'] == 'hdbscan':
        model = HDBSCAN(**technique['params']).fit(X_cls_subset)
        labels = model.labels_
    elif technique['method'] == 'spectral':
        model = SpectralClustering(**technique['params']).fit(X_cls_subset)
        labels = model.labels_
    elif technique['method'] == 'gmm':
        model = GaussianMixture(**technique['params']).fit(X_cls_subset)
        labels = model.predict(X_cls_subset)
    elif technique['method'] == 'affinity':
        model = AffinityPropagation(**technique['params']).fit(X_cls_subset)
        labels = model.labels_
        
    if len(np.unique(labels))!=1:
        sil_score = silhouette_score(X_cls_subset, labels)
        ch_score = calinski_harabasz_score(X_cls_subset, labels)
        db_score = davies_bouldin_score(X_cls_subset, labels)
    
        metrics_text = (
        f"Silhouette[-1..+1] (inter/intra distance): {sil_score:.2f}\n"
        f"Calinski-Harabasz[0..+inf] (intra/inter variance): {ch_score:.2f}\n"
        f"Davies-Bouldin[0..+inf] (centroid similarity): {db_score:.2f}"
        )
        print(metrics_text)
    
    print(f'amount labels {len(np.unique(labels))}')
    cluster_info={}  # cluster_number: {[(key_point_lat,key_point_long),(),...], initial_class_size} # no need?
    for label in np.unique(labels):
        # label is number name of cluster
        X_cls_subset_label=X_cls_subset[labels==label]
        # TODO: Take only good enough clusterizations
        
        alpha = 0.5  # Adjust: smaller = more concave, larger = convex-like
        concave_hull = alphashape(X_cls_subset_label, alpha)
        try: 
            keypoints = np.array(concave_hull.exterior.coords)
        except AttributeError:
            print("very few data")
            continue

        print(f'Reduced cluster into {len(keypoints)/X_cls_subset_label.shape[0]} of original amount points')
        cluster_info[label]=keypoints
    clusters_info[cls]=cluster_info

# Saving into parquet via pyarrow since we have nested data
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np

# Prepare flattened data
data = []
for group_name, clusters in clusters_info.items():
    for cluster_num, coords in clusters.items():
        data.append({
            'group': group_name,
            'cluster_number': cluster_num,
            'coordinates': coords.tolist()  # Convert numpy to list
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
    './data/processed/clusters.zstd',
    compression='zstd',
    compression_level=3
)

# Example query
import pyarrow.compute as pc
expr=pc.field("group")=='Business center'
print(table.filter(expr).num_rows)
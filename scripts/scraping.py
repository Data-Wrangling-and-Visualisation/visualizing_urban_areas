from DataCollector import DataCollector

dc=DataCollector()
lat=55.74802022425328
long=48.7462753296416
radius_meters=500
step_coor=0.02
info_nearby=dc.info_nearby_op(lat,long,radius_meters)
for row in info_nearby:
    print(row['name'],row['categories'],row['custom'])
print(dc.info_nearby_ors(lat,long,step_coor,step_coor))
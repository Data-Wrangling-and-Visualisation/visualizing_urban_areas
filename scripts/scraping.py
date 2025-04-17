from DataCollector import DataCollector
import json
dc=DataCollector()
lat=2.342200751007748
long=48.85951958438603
radius_meters=5000
step_coor=0.02
info_nearby_df=dc.info_nearby_op(long,lat,radius_meters,'Paris')
print(info_nearby_df.head())
print(len(info_nearby_df))
# print(dc.info_nearby_ors(lat,long,step_coor,step_coor))
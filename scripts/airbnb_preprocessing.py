import pandas as pd

file_path = "./data/airbnb_24.csv"
df = pd.read_csv(file_path)

# from csv obtained, keep only useful for clustering columns
useful_columns = [
    'ID', 'Name','Neighborhood Overview', 'Transit', 'Neighbourhood', 'City', 'State', 'Country', 'Zipcode',
    'Summary','Property Type', 'Room Type', 'Accommodates', 'Bathrooms', 'Bedrooms', 'Beds',
    'Bed Type', 'Square Feet', 'Price', 'Number of Reviews', 'Review Scores Rating',
    'Review Scores Cleanliness', 'Review Scores Location', 'Latitude', 'Longitude'
]
useful_df = df[useful_columns]

# cast to correct types
useful_df['ID']=pd.to_numeric(useful_df['ID'], downcast='integer', errors='coerce') # cast with .0 
useful_df=useful_df[useful_df['ID'].notna()] #keep only valid ids
useful_df['ID']=useful_df['ID'].astype(int) # remove .0
useful_df=useful_df.drop_duplicates(subset=['ID']) #remove duplicates

useful_df['Longitude']=pd.to_numeric(useful_df['Longitude'], downcast='float', errors='coerce')
useful_df['Accommodates']=pd.to_numeric(useful_df['Accommodates'], downcast='float', errors='coerce')
useful_df['Zipcode'] = useful_df['Zipcode'].astype(str)

# Remove separator, \n char from values
separator=','
string_columns=useful_df.columns[useful_df.dtypes == 'object'].tolist()
print('names',string_columns)
for column_name in string_columns:
    useful_df[column_name]=useful_df[column_name].str.replace(separator,' ')
    useful_df[column_name]=useful_df[column_name].str.replace('\n',' ')

# in initial data columns latitude and longitude are mixed up
useful_df.rename({'Latitude':'Longitude','Longitude':'Latitude'})

#TODO: Missing values via knn?

print(useful_df.dtypes)
print('len useful df:',len(useful_df))
# Change separator since commas appear in text columns
useful_df.to_csv('data/airbnb_24_preprocessed.csv', sep=separator, index=False)

# sanity check. Should be empty
# awk -F'|' 'NF!=25' data/airbnb_24_preprocessed.csv
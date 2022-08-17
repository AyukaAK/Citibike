#!/usr/bin/env python
# coding: utf-8

# # Analyzing the live citibike station data 
# 
# ## 1. Save the citibike capcity from July 3 - just once because it doesn't change that often
# ## 2. using google map API, convert the geo cordinate into the zipcode 
# 
# #### Station information as of July 3, 2022

# #### Set up: Import/install all the necessary things

# In[353]:


import requests
import pandas as pd


# In[354]:


#Import Googlemap
import googlemaps


# In[355]:


pip install -U googlemaps


# In[356]:


#Google map API key = AIzaSyDOSsHpaWdkEV5K8CytXP4D3tBAcPN7wJQ


# In[357]:


#Citi bike station data as of July 3, 2022
url_capacities = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"


# In[358]:


response = requests.get (url_capacities)
data = response.json()


# #### Check the Citibike station information json data

# In[359]:


print (data)


# In[360]:


print(data.keys())
print(data['data']['stations'])


# In[361]:


df = pd.DataFrame(data['data']['stations'])
df.head()


# #### Check the Citibike region json data (I will use it later to filter only the NYC stations )

# In[362]:


#Json file for the Citi bike station regions 
url_regions = "https://gbfs.citibikenyc.com/gbfs/en/system_regions.json"
response_regions = requests.get (url_regions)
data = response_regions.json()
data['data']['regions']


# #### Use the Google map API to change the geo cordinate to more useful information like zipcode for visualization

# In[363]:


#Setting up the Google Map API Key
gmaps = googlemaps.Client(key='AIzaSyDOSsHpaWdkEV5K8CytXP4D3tBAcPN7wJQ')


# In[364]:


# testing the reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.767272, -73.993929))


# In[365]:


# Look up an address with reverse geocoding - it's working
reverse_geocode = gmaps.reverse_geocode((40.767272, -73.993929), result_type="postal_code")
reverse_geocode[0]['address_components'][0]['long_name']


# In[366]:


# Add zip code to the df

def getZipCode(x):
    return gmaps.reverse_geocode((x.lat, x.lon), 
                                     result_type="postal_code")[0]['address_components'][0]['long_name']
df['zipCode'] = df.apply(getZipCode, axis=1)

df.head()


# #### Now, clean up the data! 

# In[ ]:


df.shape


# In[ ]:


# From the citibike station regions Json file
#[{'name': 'JC District', 'region_id': '70'},
#{'name': 'NYC District', 'region_id': '71'},
# {'name': '8D', 'region_id': '158'},
# {'name': 'Bronx', 'region_id': '185'},
# {'name': 'IC HQ', 'region_id': '189'},
# {'name': 'testzone', 'region_id': '190'},
# {'name': 'Hoboken District', 'region_id': '311'}]


# In[ ]:


#Drop where has_kiosk is False
df=df.loc[df["has_kiosk"] != False]


# In[ ]:


#Drop 'JC District''8D' 'IC HQ' 'testzone''Hoboken District' to only have the NYC stations
df=df.loc[df["region_id"] != '70']
df=df.loc[df["region_id"] != '158']
df=df.loc[df["region_id"] != '189']
df=df.loc[df["region_id"] != '190']
df=df.loc[df["region_id"] != '311']


# In[ ]:


df.shape


# In[ ]:


df.head()


# In[ ]:


#Drop all the unnecessary columns 
df= df.drop(['legacy_id','eightd_has_key_dispenser','rental_uris','rental_methods','electric_bike_surcharge_waiver'], axis=1)


# In[ ]:


df= df.drop(['external_id','short_name'], axis = 1)


# In[ ]:


# Save it as csv
df.to_csv('Citibike_Capacities_Cleaned.csv', index = False)


# In[ ]:


#group by the zipcode and sum up the capacity in each zipcode
zip_sum = df.groupby('zipCode').capacity.sum()
zip_sum


# In[ ]:


df.dtypes


# In[ ]:


#Merge the zip_sum into the df and call it df2
df2 = df.merge(zip_sum,
         left_on='zipCode',
         right_index=True,
         suffixes=('_original', '_zip_sum'))


# In[ ]:


df2.head()


# In[ ]:


#Save it to csv and merge it into the master df
df2.to_csv('Zip_and_total_Capacity.csv', index = False)


# In[ ]:





# In[ ]:





# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# # Analyze the live citibike data
# ## Saved the jason file every 10 minutes for 24h on July 5, 2022

# In[31]:


import requests
import pandas as pd
import datetime
import json


# In[32]:


url_status = 'https://gbfs.citibikenyc.com/gbfs/en/station_status.json'


# In[33]:


response = requests.get (url_status)
data = response.json()


# In[34]:


print (data['data']['stations'])


# In[35]:


df = pd.DataFrame(data['data']['stations'])
df


# # Step 1: prep

# In[36]:


#Save one Json file from NOW to my computer - base file
open('Live_Data/station_status.json', 'wb').write(response.content)


# In[37]:


#time stamp with the python module "datetime"
now = datetime.datetime.now()


# In[38]:


#Save each Json file from each timestamp to my computer
open('Live_Data/station_status'+str(now)+'.json', 'wb').write(response.content)


# In[39]:


#Step 1 in summary (each time I run this, the Json file gets saved from that time) 
import requests
import datetime
url_status = 'https://gbfs.citibikenyc.com/gbfs/en/station_status.json'
response = requests.get (url_status)
now = datetime.datetime.now()
open('Live_Data/station_status'+str(now)+'.json', 'wb').write(response.content)


# # Step 2: Use while loop to run step 1 every 10 min 
# ### create a file in VS code and run this code from the terminal because otherwise it freezes my jupyter notebook
# 
# import time
# import requests
# import datetime
# 
# while True:
#     time.sleep(300)
#     url_status = 'https://gbfs.citibikenyc.com/gbfs/en/station_status.json'
#     response = requests.get (url_status)
#     now = datetime.datetime.now()
#     open('Live_Data/station_status'+str(now)+'.json', 'wb').write(response.content)
#     
#     print("Printed after 300 seconds.")

# # Step 3: Use the files I got from step 2 to clean up and analyze
# 
# #### Save the files I want to use into another file because the original file is still getting live jason files

# ### Print the name of the files in the directory and create s a list

# In[42]:


#Step 1
# import OS module
import os
 
# Get the list of all files and directories
path = "/Users/ayukakawakami/Desktop/LedeProgram/Project_2/Citibike_story/Live_Data_July_5"
dir_list = os.listdir(path)
 
print("Files and directories in '", path, "' :")
 
# prints all files
print(dir_list)


#  ### Load each file from every 10 mins into a data frame and concatenate the df

# In[43]:


# dir_list is the list of all the file names
# Creating a list of dataframe: for loops to go to the each name, open that file into a data frame and add it to the list (df_list.append(df_time))
# df_all is the concatanation of all the dataframe from the df_list


df_list = []
for name in dir_list:
    # Opening JSON file
    file = open(path+ '/' +name)
  
    # returns JSON object as 
    # a dictionary
    data_time = json.load(file)
    df_time = pd.DataFrame(data_time['data']['stations'])
    df_list.append(df_time)
    
df_all = pd.concat(df_list)

df_all.head()


# In[44]:


#check to see if we got all the files included in df_all - check with the station ID 72 as an example - looks fine
df_all.loc[pd.Index([72], name="station_id")]


# In[45]:


#Change the format of ALL the last_reported (timestamp) to datetime

df_all['time'] = pd.to_datetime(df_all.last_reported, unit='s')
df_all.head()


# In[46]:


df_all.shape


# ### Clean up the data

# In[49]:


#Drop the rows where station_status is out_of_service
df_all=df_all.loc[df_all["station_status"] != 'out_of_service']
df_all.head()


# In[50]:


#check if they were dropped
df_all.shape


# In[51]:


#Drop all the unnecessary columns 
df_all= df_all.drop(['num_bikes_disabled','num_docks_disabled','is_renting','eightd_has_available_keys','is_returning', 'legacy_id', 'is_installed', 'eightd_active_station_services', 'valet'], axis=1)


# In[52]:


df_all.head()


# In[53]:


#check all the stations are active
df_all[df_all.station_status == 'active']
len(df_all.station_status == 'active')


# In[54]:


# Create a new columns showing the total docks in each station
df_all['total_docks'] = df_all['num_docks_available'] + df_all ['num_bikes_available'] + df_all ['num_ebikes_available']
df_all.head()


# In[55]:


# Create a new columns showing the percentage of docks available
df_all['per_num_docks_available'] = (df_all['num_docks_available']/df_all['total_docks']*100)
df_all.head()


# In[56]:


# Create a new columns showing the percentage of normal bikes (not the ebikes) available
df_all['per_num_bikes_available'] = (df_all['num_bikes_available']/df_all['total_docks']*100)
df_all.head()


# In[57]:


#sort by time
df_all = df_all.sort_values(by='time')
df_all


# In[58]:


#Drop all the stations where total_docks are 0 (because the time says 1970)
df_all=df_all.loc[df_all["total_docks"] !=0]
df_all.shape


# # Merge with the Station Information file "Zip_and_total_Capacity" using the station ID to add the zipcode and station address to this data frame 

# In[62]:


#load the CSV file from the station information with zipcode and adress
df_capacity = pd.read_csv("Zip_and_total_Capacity.csv")
df_capacity.head()


# In[63]:


#drop the unnecessary column
df_capacity= df_capacity.drop(['eightd_station_services'], axis=1)


# In[64]:


df_capacity.head()


# In[90]:


# in order to merge two files using the station id, station id needs to be the same data time in both file - so check that first
df_all.dtypes


# In[66]:


df_capacity.dtypes


# In[67]:


df_all["station_id"] = df_all["station_id"].astype(str).astype(int)


# In[68]:


df_all.dtypes


# In[69]:


#df_total to include everything by merging station information (zip and address) and station status (live data)
df_total = df_all.merge(df_capacity,
         left_on='station_id',
         right_on='station_id',
         suffixes=('_x', '_y'))


# In[70]:


df_total.head()


# In[71]:


df_total.shape


# In[72]:


#Drop all the duplicate rows
df_total = df_total.drop_duplicates()


# In[73]:


df_total.shape


# In[74]:


#Try filtering only one station to test if it worked - try the station ID 531
df_total.query("station_id == 531")


# # Any noticable trends?

# In[75]:


# Which station has the most bike capacities?
df_total.total_docks.max()


# In[76]:


# Ok, I'll focus on this most popular station as a visualization!!!
df_total.query("total_docks == 121")


# In[77]:


# Station ID 422 in midtown has the highest numbers of bike available
# Sort by time to visualize the capacity by time
df_total.sort_values(by='time', ascending = False).query("station_id == 422")


# In[78]:


# Just checking
df_total.sort_values(by='total_docks', ascending = False)


# In[79]:


#Average number of bike capacity
df_total.total_docks.mean()


# # Save the master file

# In[ ]:


#Save the CSV file for ALL the station status
df_total.to_csv('Station_Status_Master.csv', index = False)


# # Analyze the most popular station

# In[80]:


#Highest bike capacity - the most popular
df_station422 = df_total.sort_values(by='time', ascending = False).query("station_id == 422")


# In[81]:


df_station422 = df_station422.drop(['station_status', 'last_reported', 'lon', 'has_kiosk', 'station_type', 'lat', 'region_id' ], axis=1)


# In[82]:


#Save the CSV file for the station 422 
df_station422.to_csv('station422.csv', index = False)


# # Let's see if I find anything else interesting..

# In[83]:


#Any other interesting stations?
#Try filtering only for zipcode 10027 of Columbia University
df_Columbia_Station = df_total.query("zipCode == 10027")
df_Columbia_Station.head()


# In[84]:


#a citibike station near Columbia on W 116 St & Broadway
df_Columbia_Station_broadway = df_total.query("station_id == 3536")
df_Columbia_Station_broadway.head()


# In[85]:


df_Columbia_Station_broadway= df_Columbia_Station_broadway.drop(['station_status', 'last_reported', 'lon', 'has_kiosk', 'station_type', 'lat', 'region_id' ], axis=1)


# In[86]:


df_Columbia_Station_broadway.head()


# In[87]:


#Save the CSV file for Columbia_Station_broadway
df_Columbia_Station_broadway.to_csv('Columbia_Station_broadway.csv', index = False)


# In[88]:


#a citibike station near Columbia on W 116 St & Amsterdam Ave
df_Columbia_Station_amsterdam = df_total.query("station_id == 3539")
df_Columbia_Station_amsterdam.head()


# In[ ]:


df_Columbia_Station_amsterdam.head()


# In[ ]:


#Save the CSV file for Columbia_Station_broadway
df_Columbia_Station_amsterdam.to_csv('Columbia_Station_amsterdam.csv', index = False)


# In[ ]:


#group by time for the percentage of bike available 
per_bike = df_total.groupby('time').per_num_bikes_available.mean()
per_bike


# In[ ]:


#Merge 
df_per_bike = df_total.merge(per_bike,
         left_on='time',
         right_index=True,
         suffixes=('_original', '_per_bike'))


# In[ ]:


df_per_bike


# In[ ]:


#Save the csv
df_per_bike.to_csv('Per_bike_bytime.csv', index = False)


# In[ ]:


df_bike_per_time = pd.read_csv('Per_bike_bytime.csv')
df_bike_per_time.head()


# In[ ]:


df_bike_per_time.= df_bike_per_time.drop(['num_docks_available','num_bikes_available','station_id','num_ebikes_available','station_status','last_reported','total_docks','per_num_docks_available','name','lon','has_kiosk','station_type','lat','region_id','capacity_original','zipCode','capacity_zip_sum'], axis=1)


# In[152]:


df_capa_zip = pd.read_csv("Station_Capacity_by_Zip.csv")
df_capa_zip = df_capa_zip.drop_duplicates()


# In[137]:


df_capa_zip.to_csv('Capacity_by_zip.csv', index = False)


# In[ ]:


#Save the CSV file for the station status near Columbia University
df_Columbia_Station.to_csv('Station_Status_Columbia.csv', index = False)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





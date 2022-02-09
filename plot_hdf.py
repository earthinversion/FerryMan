
# coding: utf-8

# In[123]:


from pyhdf import SD
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
from glob import glob


# Fireants information
# https://www.cabi.org/ISC/datasheet/50569
# 
# *Climate	Status	Description	Remark
# 
# A - Tropical/Megathermal climate	Preferred	Average temp. of coolest month > 18°C, > 1500mm precipitation annually	
# Af - Tropical rainforest climate	Preferred	> 60mm precipitation per month	
# Am - Tropical monsoon climate	Preferred	Tropical monsoon climate ( < 60mm precipitation driest month but > (100 - [total annual precipitation(mm}/25]))	
# As - Tropical savanna climate with dry summer	Tolerated	< 60mm precipitation driest month (in summer) and < (100 - [total annual precipitation{mm}/25])	
# Aw - Tropical wet and dry savanna climate	Tolerated	< 60mm precipitation driest month (in winter) and < (100 - [total annual precipitation{mm}/25])	
# B - Dry (arid and semi-arid)	Tolerated	< 860mm precipitation annually	
# C - Temperate/Mesothermal climate	Tolerated	Average temp. of coldest month > 0°C and < 18°C, mean warmest month > 10°C	
# Cf - Warm temperate climate, wet all year	Tolerated	Warm average temp. > 10°C, Cold average temp. > 0°C, wet all year	
# *Air Temperature
# 
# Parameter	Lower limit	Upper limit
# 
# Mean annual temperature (ºC)	3.6	40.6
# 

# Indian-tree spurge https://www.cabi.org/ISC/datasheet/21381
#     
# *Climate	Status	Description	Remark
# As - Tropical savanna climate with dry summer	Tolerated	< 60mm precipitation driest month (in summer) and < (100 - [total annual precipitation{mm}/25])	
# Aw - Tropical wet and dry savanna climate	Tolerated	< 60mm precipitation driest month (in winter) and < (100 - [total annual precipitation{mm}/25])	
# BS - Steppe climate	Preferred	> 430mm and < 860mm annual precipitation	
# BW - Desert climate	Tolerated	< 430mm annual precipitation	
# Cs - Warm temperate climate with dry summer	Preferred	Warm average temp. > 10°C, Cold average temp. > 0°C, dry summers	
# Cw - Warm temperate climate with dry winter	Preferred	Warm temperate climate with dry winter (Warm average temp. > 10°C, Cold average temp. > 0°C, dry winters)	
# Cf - Warm temperate climate, wet all year	Tolerated	Warm average temp. > 10°C, Cold average temp. > 0°C, wet all year	
# 
# Air Temperature
# 
# Mean annual temperature (ºC)	21	28

# In[125]:


file_list = glob("MOD*.hdf")
for i,file in enumerate(file_list):
    hdf = SD.SD(file)
    data_day = hdf.select('LST_Day_CMG')
    data_night = hdf.select('LST_Night_CMG')
    temp_day=np.array(data_day[:,:],np.float)
    temp_night=np.array(data_night[:,:],np.float)
    temp = (temp_day + temp_night)/2
    temp[np.where(temp==0)]=np.nan

    temp = temp *0.02 - 273.15

    if i == 0:
        temp_total = temp
    else:
        temp_total += temp
temp_total = temp_total/12
temp_total[np.where(temp_total<lowtemp)]=np.nan
temp_total[np.where(temp_total>uptemp)]=np.nan


# In[124]:


#Pest information
#Fire ants
#https://www.cabi.org/ISC/datasheet/50569
#lowtemp = 3.6
#uptemp = 40.6

#Black rat
#


# In[132]:


plt.figure(figsize=(20,20))
m = Basemap(projection='cyl', resolution = 'l',
    llcrnrlat=-90, urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180)

m.drawcountries()
m.drawcoastlines(linewidth=0.5)
cs = m.imshow(np.flipud(temp_total),cmap="jet")
cbar = m.colorbar(cs,location="right")
cbar.set_label(r"Temperature $^oC$",fontsize = 20)
plt.title("Temperature preferred region of black rat", fontsize = 20)
plt.savefig("fireants_temp.png",bbox_inches = "tight")
plt.show()


# In[131]:


dic = hdf.datasets()
print(dic.keys())


# In[142]:


import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import h5py


# In[153]:


import os

import h5py
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

def run(FILE_NAME):
    
    with h5py.File(FILE_NAME, mode='r') as f:

        name = '/Grid/precipitation'
        data = f[name][:]
        units = f[name].attrs['units']
        _FillValue = f[name].attrs['_FillValue']
        data[data == _FillValue] = np.nan
        data = np.ma.masked_where(np.isnan(data), data)

        
        # Get the geolocation data
        latitude = f['/Grid/lat'][:]
        longitude = f['/Grid/lon'][:]
        return f
    plt.figure(figsize=(20,10))    
    m = Basemap(projection='cyl', resolution='l',
                llcrnrlat=-90, urcrnrlat=90,
                llcrnrlon=-180, urcrnrlon=180)
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(-90, 91, 45))
    m.drawmeridians(np.arange(-180, 180, 45), labels=[True,False,False,True])
    m.pcolormesh(longitude, latitude, data.T, latlon=True)
    cb = m.colorbar()    
    cb.set_label(units)

    basename = os.path.basename(FILE_NAME)
    plt.title('{0}\n{1}'.format(basename, name))
    fig = plt.gcf()
    plt.show()
    
    


# In[154]:


f = run("3B-MO.MS.MRG.3IMERG.20170501-S000000-E235959.05.V05B.HDF5")


# In[179]:


f = h5py.File("3B-MO.MS.MRG.3IMERG.20161201-S000000-E235959.12.V05B.HDF5","r")


# In[186]:


list(f['Grid'].keys())


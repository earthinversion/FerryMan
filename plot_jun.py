
# coding: utf-8

# In[ ]:


from pyhdf import SD
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import ticker
from glob import glob
from mpl_toolkits.basemap import Basemap
import os, h5py, time
import multiprocessing
from multiprocessing import Pool, TimeoutError
import csv, sys
import pandas as pd


# In[15]:


path_to_data = 'Data/NASA'
path_to_param = 'speices_parameters.csv'
path_to_loc = 'Analysis'

# get temperature data
def get_temperature(filename):

    hdf = SD.SD(filename)
    data_day = hdf.select('LST_Day_CMG')
    data_night = hdf.select('LST_Night_CMG')
    temp_day=np.array(data_day[:,:],np.float)
    temp_night=np.array(data_night[:,:],np.float)
    temp_day[np.where(temp_day==0)]=np.nan
    temp_night[np.where(temp_night==0)]=np.nan

    temp_day = temp_day *0.02 - 273.15
    temp_night = temp_night *0.02 - 273.15

    temp_day = np.flipud(temp_day)
    temp_day = temp_day[0:-1:2,0:-1:2]
    temp_dimension = temp_day.shape

    temp_night = np.flipud(temp_night)
    temp_night = temp_night[0:-1:2,0:-1:2]

    lat = np.linspace(-90, 90, temp_dimension[0])
    lon = np.linspace(-180, 180, temp_dimension[1])

    #generate lon and lat mesh for temperature
    temp_lon, temp_lat = np.meshgrid(lon, lat)

    return temp_lat, temp_lon, temp_day, temp_night

# get precipitation data
def get_precipitation(filename):

    with h5py.File(filename, mode='r') as f:

        name = '/Grid/precipitation'
        data = f[name][:]
        units = f[name].attrs['units']
        _FillValue = f[name].attrs['_FillValue']
        data[data == _FillValue] = np.nan
        data = np.ma.masked_where(np.isnan(data), data)

        # Get the geolocation data
        prec_lat = f['/Grid/lat'][:]
        prec_lon = f['/Grid/lon'][:]
        precipitation = data.T * 30. * 24. # convert rate to precipitation

    return prec_lat, prec_lon, precipitation


def get_ti(td,tn,dv):
    shp = td.shape
    ti = np.zeros(shp,dtype=np.float)

    for j in range(shp[0]):
        for i in range(shp[1]):
            hi_temp = td[j,i]
            low_temp = tn[j,i]

            ti[j,i] = ( hi_temp + low_temp ) / 2
    return ti

def get_mi(prec,sm):
    shp = prec.shape
    mi = np.zeros(shp,dtype=np.float)

    for j in range(shp[0]):
        for i in range(shp[1]):
            mi[j,i] = prec[j,i]

    return mi

df_sp = pd.read_csv(path_to_param,encoding="iso-8859-1")

scientific_name = df_sp['scientific_name']
nick_name = df_sp['nick_name']
nspe = len(nick_name)
spe_dv = np.zeros((nspe,4))
spe_sm = np.zeros((nspe,4))
for i in range(4):
    spe_dv[:,i] = df_sp['dv_%d' % i]
    spe_sm[:,i] = df_sp['sm_%d' % i]

file_speloc = []
for i in range(nspe):
    name = scientific_name[i].replace("_"," ").capitalize() + '.csv'
    file_speloc.append(name)

file_temp = glob(path_to_data + 'MOD*2017*')
file_temp.sort()
file_prec = glob(path_to_data + '3B*2017*')
file_prec.sort()
nmonth = len(file_temp)

lon = np.linspace(-180, 180, 3600)
lat = np.linspace(-90, 90, 1800)
lon, lat = np.meshgrid(lon, lat)

time_tag1 = time.clock()

for month in range(nmonth):
    # month += 11
    temp_lat, temp_lon, temp_day, temp_night = get_temperature(file_temp[month])
    prec_lat, prec_lon, prec_raw = get_precipitation(file_prec[month])

    MI = np.zeros(temp_day.shape,dtype=np.float)

    prec_raw.mask = ma.nomask
    precipitation = np.array(prec_raw)
    precipitation[precipitation==np.nan] = 0.

    print ('\nMonth: %2d' % (month + 1))
    for spe in range(1):

        print ('%d: ' % (spe+1) + scientific_name[spe].replace("_"," ").capitalize())

        time_tag2 = time.clock()
        dv = spe_dv[spe,:]
        sm = spe_sm[spe,:]

        pool = Pool(processes=4)
        nblock = 12
        interval = int(1800/nblock)

        print ('** Start to calculate EI.')
        # result_ti = []
        result_mi = []
        for b in range(nblock):
            # td_b = temp_day[b*interval:(b+1)*interval,:]
            # tn_b = temp_night[b*interval:(b+1)*interval,:]
            # result_ti.append(pool.apply_async(get_ti, (td_b,tn_b,dv)))

            mi_b = precipitation[b*interval:(b+1)*interval,:]
            result_mi.append(pool.apply_async(get_mi, (mi_b,sm)))

        for b in range(nblock):
            # TI[b*interval:(b+1)*interval,:] = result_ti[b].get()
            MI[b*interval:(b+1)*interval,:] = result_mi[b].get()

        # clean up
        pool.close()
        pool.join()

        # GI = MI * TI * 100

        print ('** Start to plot data.')

        df_sp = pd.read_csv(file_speloc[spe],
                            skiprows = 2,
                            encoding="iso-8859-1")

        fig = plt.figure(figsize=(20,10))
        m = Basemap(projection='cyl', resolution='l',
                    llcrnrlat=-90, urcrnrlat=90,
                    llcrnrlon=-180, urcrnrlon=180)
        m.drawcoastlines(linewidth=0.5,zorder=2)

        # TI[TI==0] = -1
        mi_plot = plt.contourf(lon, lat, MI, 
                                cmap="ocean_r",
                                vmax=1000,vmin=0,
                                levels=np.linspace(0,1000,101),
                                extend='neither',
                                zorder=1)

        cb = m.colorbar(mi_plot)
        cb.set_label(r'Monthly Precipitation (mm)', fontsize = 20)
        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator = tick_locator
        cb.update_ticks()

        spe_lon = df_sp["Longitude"]
        spe_lat = df_sp["Latitude"]
        lon_ = [];lat_ = []
        for x, y in zip(spe_lon,spe_lat):
            try:
                xx, yy = m(float(x),float(y))
                lon_.append(xx);lat_.append(yy)
            except:
                pass
        m.scatter(lon_, lat_, marker = "o" ,
                    s=50, c="r", zorder=3,
                    edgecolors = "k",
                    label = "Species occurrence")

        plt.legend(fontsize=20)
        plt.savefig(scientific_name[spe] + "_%2.2d_MI.png" % (1 + month), bbox_inches = "tight")
        plt.close()

        print('Spent Time: %4.1fs (total: %6.1fs)' % (time.clock() - time_tag2, time.clock() - time_tag1))



# In[ ]:


c


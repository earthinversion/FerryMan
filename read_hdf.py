#!/usr/bin/env python3

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

path_to_data  = './Data/NASA'
path_to_param = './speices_parameters.csv'
path_to_loc   = './Data/Species'

# get temperature data
def get_temperature(filename):

    hdf = SD.SD(filename)
    #datasets_dic = hdf.datasets()
    #for idx,sds in enumerate(datasets_dic.keys()):
    #    print (idx,sds)

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
        #        print (units)
        #        print (list(f['Grid'].keys()))

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
            dt = hi_temp - low_temp
            if dt > 0:
                iq = min( 1, 12 * max(0, hi_temp - dv[0]) ** 2 / dt / ((dv[1] - dv[0]) * 24))
            else:
                iq = np.nan
            ih = min( 1 - ( max(0, hi_temp - dv[2]) / (dv[3] - dv[2])) , 1)
            ti[j,i] = iq * ih
    return ti

def get_mi(prec,sm):
    shp = prec.shape
    mi = np.zeros(shp,dtype=np.float)

    for j in range(shp[0]):
        for i in range(shp[1]):
            m = prec[j,i]
            if m < sm[0]:
                mi_index = 0
            elif m < sm[1]:
                mi_index = (m - sm[0])/(sm[1] - sm[0])
            elif m < sm[2]:
                mi_index = 1.
            elif m < sm[3]:
                mi_index = (m - sm[3])/(sm[2] - sm[3])
            else:
                mi_index = 0.
            mi[j,i] = mi_index

    return mi

def main():

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
        name = '/' + scientific_name[i].replace("_"," ").capitalize() + '.csv'
        file_speloc.append(path_to_loc + name)

    file_temp = glob(path_to_data + '/MOD*2017*')
    file_temp.sort()
    file_prec = glob(path_to_data + '/3B*2017*')
    file_prec.sort()
    nmonth = len(file_temp)

    lon = np.linspace(-180, 180, 3600)
    lat = np.linspace(-90, 90, 1800)
    lon, lat = np.meshgrid(lon, lat)

    time_tag1 = time.clock()

    for month in range(nmonth):
#        month += 
        temp_lat, temp_lon, temp_day, temp_night = get_temperature(file_temp[month])
        prec_lat, prec_lon, prec_raw = get_precipitation(file_prec[month])

        TI = np.zeros(temp_day.shape,dtype=np.float)
        MI = np.zeros(temp_day.shape,dtype=np.float)

        prec_raw.mask = ma.nomask
        precipitation = np.array(prec_raw)
        precipitation[precipitation==np.nan] = 0.

        print ('\nMonth: %2d' % (month + 1))
        for spe in range(6):
#            spe += 6
            print ('%d: ' % (spe+1) + scientific_name[spe].replace("_"," ").capitalize())

            time_tag2 = time.clock()
            dv = spe_dv[spe,:]
            sm = spe_sm[spe,:]

            nblock = 12
            interval = int(1800/nblock)

            pool = Pool(processes=4)
            print ('** Start to calculate EI.')

            result_ti = []
            result_mi = []
            for b in range(nblock):
                td_b = temp_day[b*interval:(b+1)*interval,:]
                tn_b = temp_night[b*interval:(b+1)*interval,:]
                result_ti.append(pool.apply_async(get_ti, (td_b,tn_b,dv)))

                mi_b = precipitation[b*interval:(b+1)*interval,:]
                result_mi.append(pool.apply_async(get_mi, (mi_b,sm)))

            for b in range(nblock):
                TI[b*interval:(b+1)*interval,:] = result_ti[b].get()
                MI[b*interval:(b+1)*interval,:] = result_mi[b].get()

            # clean up
            pool.close()
            pool.join()


            GI = MI * TI * 100

            print ('** Start to plot data.')


            fig = plt.figure(figsize=(20,10))
            m = Basemap(projection='cyl', resolution='l',
                        llcrnrlat=-90, urcrnrlat=90,
                        llcrnrlon=-180, urcrnrlon=180)
            m.drawcoastlines(linewidth=0.5,zorder=2)

            GI[GI==0] = -1
            gi_plot = plt.contourf(lon, lat, GI, 
                                    cmap="Greens",
                                    vmax=100,vmin=0,
                                    levels=np.linspace(0,100,101),
                                    extend='neither',
                                    zorder=1)

            cb = m.colorbar(gi_plot)
            cb.set_label(r'Ecoclimatic Index (%)', fontsize = 20)
            tick_locator = ticker.MaxNLocator(nbins=5)
            cb.locator = tick_locator
            cb.update_ticks()

            if spe != 6:
                df_sp = pd.read_csv(file_speloc[spe],
                                    skiprows = 2,
                                    encoding="iso-8859-1")

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
            plt.savefig(scientific_name[spe] + "_%2.2d.png" % (1 + month),bbox_inches = "tight")
            plt.close()

            print('Spent Time: %4.1fs (total: %6.1fs)' % (time.clock() - time_tag2, time.clock() - time_tag1))


        




    sys.exit()

    if 0:
        fig = plt.figure(figsize=(20,20))

        ax_temp = plt.subplot2grid((12, 6), (6, 0), rowspan=1, colspan=3)
        ax_temp.set_title("Temperature", fontsize = 20)

        ax_prec = plt.subplot2grid((12, 6), (5, 0), rowspan=1, colspan=3)
        plt.title("Precipitation", fontsize = 20)

        ax_ti = plt.subplot2grid((12, 6), (4, 0), rowspan=1, colspan=3)
        plt.title("TI", fontsize = 20)

        ax_mi = plt.subplot2grid((12, 6), (3, 0), rowspan=1, colspan=3)
        plt.title("MI", fontsize = 20)

        ax_gi = plt.subplot2grid((12, 6), (2, 0), rowspan=1, colspan=3)
        plt.title("GI", fontsize = 20)

        ax3 = plt.subplot2grid((12, 6), (7,  5), rowspan=1, colspan=1)
        ax4 = plt.subplot2grid((12, 6), (8,  5), rowspan=1, colspan=1)
        ax5 = plt.subplot2grid((12, 6), (9,  5), rowspan=1, colspan=1)
        ax6 = plt.subplot2grid((12, 6), (10,  5), rowspan=1, colspan=1)
        ax7 = plt.subplot2grid((12, 6), (11,  5), rowspan=1, colspan=1)


        temp_plot = ax_temp.contourf(lon, lat, (temp_day+temp_night)/2,cmap="jet")

        prec_plot = ax_prec.contourf(lon, lat, precipitation,cmap="jet")

        ti_max, ti_min = 1 , 0
        ti_nl = 101
        color_ti = 'jet'
        orientation = 'vertical'
        cm = plt.cm.get_cmap(color_ti,ti_nl)
        TI[TI==0] = -1
        ti_plot = ax_ti.contourf(lon, lat, TI, levels=np.linspace(ti_min,ti_max,ti_nl),extend='neither',cmap=cm,vmax=ti_max,vmin=ti_min)

        mi_max, mi_min = 1 , 0
        mi_nl = 101
        color_mi = 'jet'
        orientation = 'vertical'
        cm = plt.cm.get_cmap(color_mi,mi_nl)
        MI[MI==0] = -1
        mi_plot = ax_mi.contourf(lon, lat, MI, levels=np.linspace(mi_min,mi_max,mi_nl),extend='neither',cmap=cm,vmax=mi_max,vmin=mi_min)

        gi_max, gi_min = 100 , 0
        gi_nl = 101
        color_gi = 'jet'
        orientation = 'vertical'
        cm = plt.cm.get_cmap(color_gi,gi_nl)
        GI[GI==0] = -1
        gi_plot = ax_gi.contourf(lon, lat, GI, levels=np.linspace(gi_min,gi_max,gi_nl),extend='neither',cmap=cm,vmax=gi_max,vmin=gi_min)


        cb = fig.colorbar(temp_plot, cax=ax3,orientation=orientation)
        cb.set_label(r'Temperature')
        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator = tick_locator
        cb.update_ticks()

        cb = fig.colorbar(prec_plot, cax=ax4,orientation=orientation)
        cb.set_label(r'Precipitation')
        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator = tick_locator
        cb.update_ticks()

        cb = fig.colorbar(ti_plot, cax=ax5,orientation=orientation)
        cb.set_label(r'TI')
        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator = tick_locator
        cb.update_ticks()

        cb = fig.colorbar(mi_plot, cax=ax6,orientation=orientation)
        cb.set_label(r'MI')
        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator = tick_locator
        cb.update_ticks()

        cb = fig.colorbar(gi_plot, cax=ax7,orientation=orientation)
        cb.set_label(r'GI')
        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator = tick_locator
        cb.update_ticks()

        ax1_left, ax1_bot, ax1_width, ax1_height = 0.05, 0.75, 0.35, 0.18
        ax_temp.set_position( [ax1_left,   ax1_bot     , ax1_width, ax1_height])
        ax_prec.set_position([ax1_left,    ax1_bot-0.23, ax1_width, ax1_height])
        ax_ti.set_position([ax1_left+0.45, ax1_bot     , ax1_width, ax1_height])
        ax_mi.set_position([ax1_left+0.45, ax1_bot-0.23, ax1_width, ax1_height])
        ax_gi.set_position([ax1_left+0.45, ax1_bot-0.46, ax1_width, ax1_height])

        lg_left, lg_bot, lg_width, lg_height = 0.42, 0.75, 0.02, 0.18
        ax3.set_position([lg_left      , lg_bot      , lg_width,lg_height])
        ax4.set_position([lg_left      , lg_bot-0.23 , lg_width,lg_height])
        ax5.set_position([lg_left+0.45 , lg_bot      , lg_width,lg_height])
        ax6.set_position([lg_left+0.45 , lg_bot-0.23 , lg_width,lg_height])
        ax7.set_position([lg_left+0.45 , lg_bot-0.46 , lg_width,lg_height])
      


        plt.savefig("fireants_pres.png")    

if __name__ == '__main__':

    main()



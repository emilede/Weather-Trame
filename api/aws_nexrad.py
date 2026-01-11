import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates

import cartopy.crs as ccrs
import pyart
import pandas as pd

import nexradaws
import tempfile
import pytz

templocation = tempfile.mkdtemp()

import cartopy.feature as cfeature
from metpy.plots import USCOUNTIES

### Define the radar, start time and end time
radar_id = 'KDVN'
start = pd.Timestamp(2020,8,10,16,30).tz_localize(tz='UTC')
end = pd.Timestamp(2020,8,10,21,0).tz_localize(tz='UTC')

### Bounds of map we want to plot
min_lon = -93.25
max_lon = -88.
min_lat = 40.35
max_lat = 43.35


#### and get the data
conn = nexradaws.NexradAwsInterface()
scans = conn.get_avail_scans_in_range(start, end, radar_id)
print("There are {} scans available between {} and {}\n".format(len(scans), start, end))
print(scans[0:4])

## download these files
#results = conn.download(scans[0:2], templocation)
results = conn.download(scans, templocation)

### wind reports
wind_rpts = pd.read_csv("https://www.spc.noaa.gov/wcm/data/"+str(start.year)+"_wind.csv")

wind_rpts['datetime'] = pd.to_datetime(wind_rpts.date + ' ' + wind_rpts.time) ## convert to datetime
wind_rpts.set_index("datetime",inplace=True)

### times in the file are given in central standard time (UTC+6). Localize, and convert to UTC
wind_rpts.index = wind_rpts.index.tz_localize("Etc/GMT+6",ambiguous='NaT',nonexistent='shift_forward').tz_convert("UTC")

## subset down to 30 minutes before/after the radar times we're plotting
wind_rpts = wind_rpts[((start-pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")):((end+pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"))]
wind_rpts

### repeat for tornado reports
tor_rpts = pd.read_csv("https://www.spc.noaa.gov/wcm/data/"+str(start.year)+"_torn.csv")

tor_rpts['datetime'] = pd.to_datetime(tor_rpts.date + ' ' + tor_rpts.time) ## convert to datetime
tor_rpts.set_index("datetime",inplace=True)

### times in the file are given in central standard time (UTC+6). Localize, and convert to UTC
tor_rpts.index = tor_rpts.index.tz_localize("Etc/GMT+6",ambiguous='NaT',nonexistent='shift_forward').tz_convert("UTC")

## subset down to 30 minutes before/after the radar times we're plotting
tor_rpts = tor_rpts[((start-pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")):((end+pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"))]
tor_rpts

### repeat for hail
hail_rpts = pd.read_csv("https://www.spc.noaa.gov/wcm/data/"+str(start.year)+"_hail.csv")

hail_rpts['datetime'] = pd.to_datetime(hail_rpts.date + ' ' + hail_rpts.time) ## convert to datetime
hail_rpts.set_index("datetime",inplace=True)

### times in the file are given in central standard time (UTC+6). Localize, and convert to UTC
hail_rpts.index = hail_rpts.index.tz_localize("Etc/GMT+6",ambiguous='NaT',nonexistent='shift_forward').tz_convert("UTC")

## subset down to 30 minutes before/after the radar times we're plotting
hail_rpts = hail_rpts[((start-pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")):((end+pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"))]
hail_rpts

### loop over the radar images that have been downloaded

for i,scan in enumerate(results.iter_success(),start=1):
#for i in range(0,1):
    ## skip the files ending in "MDM"
    if scan.filename[-3:] != "MDM":
        
        print(str(i))
        print("working on "+scan.filename)
        
        this_time = pd.to_datetime(scan.filename[4:17], format="%Y%m%d_%H%M").tz_localize("UTC")
    
        radar = scan.open_pyart()
        #display = pyart.graph.RadarDisplay(radar)

        fig = plt.figure(figsize=[15, 7])

        map_panel_axes = [0.05, 0.05, .4, .80]
        x_cut_panel_axes = [0.55, 0.10, .4, .25]
        y_cut_panel_axes = [0.55, 0.50, .4, .25]

        projection = ccrs.PlateCarree()

        ## apply gatefilter (see here: https://arm-doe.github.io/pyart/notebooks/masking_data_with_gatefilters.html)
        #gatefilter = pyart.correct.moment_based_gate_filter(radar)
        gatefilter = pyart.filters.GateFilter(radar)

        # Lets remove reflectivity values below a threshold.
        gatefilter.exclude_below('reflectivity', -2.5)

        display = pyart.graph.RadarMapDisplay(radar)
       
        ### set up plot
        ax1 = fig.add_axes(map_panel_axes, projection=projection)
        
        # Add some various map elements to the plot to make it recognizable.
        ax1.add_feature(USCOUNTIES.with_scale('500k'), edgecolor="gray", linewidth=0.4)
        #ax1.coastlines('50m', edgecolor='black', linewidth=0.75)
        ax1.add_feature(cfeature.STATES.with_scale('10m'), linewidth=1.0)
    
        cf = display.plot_ppi_map('reflectivity', 0, vmin=-7.5, vmax=65,
                          min_lon=min_lon, max_lon=max_lon, min_lat=min_lat, max_lat=max_lat,
                          title=radar_id+" reflectivity and severe weather reports, "+this_time.strftime("%H%M UTC %d %b %Y"),
                          projection=projection, resolution='10m',
                             gatefilter=gatefilter,
                          cmap='pyart_HomeyerRainbow', 
                          colorbar_flag=False,
                          lat_lines=[0,0], lon_lines=[0,0]) ## turns off lat/lon grid lines
        #display.plot_crosshairs(lon=lon, lat=lat)
        
        ## plot horizontal colorbar 
        display.plot_colorbar(cf,orient='horizontal', pad=0.07)
        
        # Plot range rings if desired
        #display.plot_range_ring(25., color='gray', linestyle='dashed')
        #display.plot_range_ring(50., color='gray', linestyle='dashed')
        #display.plot_range_ring(100., color='gray', linestyle='dashed')

        ax1.set_xticks(np.arange(min_lon, max_lon, .5), crs=ccrs.PlateCarree())
        ax1.set_yticks(np.arange(min_lat, max_lat, .5), crs=ccrs.PlateCarree())     
       
        ## add marker points for severe reports
        wind_rpts_now = wind_rpts[((start-pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")):this_time.strftime("%Y-%m-%d %H:%M")]
        ax1.scatter(wind_rpts_now.slon.values.tolist(), wind_rpts_now.slat.values.tolist(), s=20, facecolors='none', edgecolors='mediumblue', linewidths=1.8)
        tor_rpts_now = tor_rpts[((start-pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")):this_time.strftime("%Y-%m-%d %H:%M")]
        ax1.scatter(tor_rpts_now.slon.values.tolist(), tor_rpts_now.slat.values.tolist(), s=20, facecolors='red', edgecolors='black', marker="v",linewidths=1.5)
        hail_rpts_now = hail_rpts[((start-pd.Timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")):this_time.strftime("%Y-%m-%d %H:%M")]
        ax1.scatter(hail_rpts_now.slon.values.tolist(), hail_rpts_now.slat.values.tolist(), s=20, facecolors='none', edgecolors='green', linewidths=1.8)

        
        plt.savefig(scan.radar_id+"_"+scan.filename[4:17]+"_dz_rpts.png",bbox_inches='tight',dpi=300,
                   facecolor='white', transparent=False)
        #plt.show()
        plt.close('all')
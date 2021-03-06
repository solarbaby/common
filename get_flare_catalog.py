import os
from datetime import datetime
import pickle
from urllib.request import urlopen
import pandas as pd
import numpy as np
import math

def create_datetime(ymd, hm):
    date=[]
    #unpack ymd and fix year

    for item, ihm in zip(ymd, hm):
        if item=="  ":
            date.append(None)
            continue
        
        datestr=item.split()
        
        year=int(datestr[0])
        month=int(datestr[1])
        day=int(datestr[2])

        #fix two year dates without messing up 4 year dates
        if year<70: 
            year=year+2000
        elif  year<100: 
            year+=1900
        
        if math.isnan(ihm)==False:
            hour=math.floor(ihm/100)
            minute=math.floor(ihm-hour*100)

            #now check to see if the time is past 2400 and adjust
            if hour>=24:
                hour-=24
                day+=1
                [day, month, year]=check_daymonth(day, month, year)
            try:
                date.append(datetime(year, month, day, hour, minute))
            except:
                date.append(np.nan)
        else:
            date.append(np.nan)
    return date

def check_daymonth(day, month, year):
    if (day==32 or (day==31 and (month==9 or month==4 or
    month==6 or month==11)) or (day==30 and month==2) or
    (month==2 and day==29 and year % 4 ==0)):
        day=1
        month=month+1
    if month==13:
        year=year+1
        month=1
    return [day, month, year]
        
                
def download_flare_catalog(start_year, stop_year):
    """ program to read in GOES h-alpha and x-ray flare information from web"""
    """ usage: [ha, xray]=get_flare_catalog; ha is a pandas dataframe"""
    """ ha['location'][300] prints the 300th location"""

    count=0
    #strange character at the end of teh 2003 file causes trouble
    for getyear in range(start_year, stop_year):  
        print("year: ", getyear)
        web_stem="http://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/"
        xray_webpage=web_stem+"goes-xrs-report_"+str(getyear)+".txt"
        web_stem="https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/h-alpha/reports/kanzelhohe/halpha-flare-reports_kanz_"
        ha_webpage=web_stem+str(getyear)+".txt"
        print(xray_webpage)
        print(ha_webpage)
               
        names=["data code", "station code", "year", "month", "day", "init_ind", "init_time", "final_ind", "final_time", "peak_ind", 
               "peak_time", "location", "optical", "something", "xray_class", "xray_size", "station", "blank", "NOAA_AR", "etc"]
    
        widths=[2, 3, 2, 2, 2, 2, 4, 1, 4, 1, 4, 7, 3, 22, 1, 3, 8, 8, 6, 24]
        xray_df_year=pd.read_fwf(xray_webpage, widths=widths, header=None, names=names)#, parse_dates=[[2, 3, 4]])
        xray_df_year["year_month_day"]=[str(x)+" "+str(y)+" "+str(z) for x,y,z in zip(xray_df_year["year"], xray_df_year["month"], xray_df_year["day"])]


        
        xray_df_year["init_date"]=create_datetime(xray_df_year["year_month_day"], xray_df_year["init_time"])
        xray_df_year["peak_date"]=create_datetime(xray_df_year["year_month_day"], xray_df_year["peak_time"])
        xray_df_year["final_date"]=create_datetime(xray_df_year["year_month_day"], xray_df_year["final_time"])
        xray_df_year["location"]=[x if str(x)[0]=="N" or str(x)[0]=="S" else None for x in xray_df_year["location"]]

        xray_df_year=xray_df_year[["init_date", "peak_date", "final_date", "location", "xray_class", "xray_size", "NOAA_AR"]]

        if count==0:

            xray_df=xray_df_year
            count=1
        else:
#            dfs=[ha_df, ha_df_year]
#            ha_df=pd.concat(dfs)
            dfs=[xray_df, xray_df_year]
            xray_df=pd.concat(dfs)
    ha_df="not yet implemented"
    return (xray_df, ha_df)

        
def get_flare_catalog_fromfile():
    """ program to read in GOES h-alpha and x-ray flare information from file"""
    """ usage: [ha, xray]=get_flare_catalog; ha is a dict"""
    """ ha['location'][300] prints the 300th location"""
    """ keys are ha.keys() -- station_num, group_num, initial_time, final_time"""
    """ peak_time, optical_importance, optical_brightness, xray_class, """
    """ xray_size, NOAA_AR """
    #define data file location
    data_dir=os.getcwd()+"/data"
#    data_dir="/Users/alyshareinard/Documents/python/common/data"
    ha_file=data_dir+"/ha.txt"
    xray_file=data_dir+"/xray.txt"

    #code to read in xray data
    names=["data code", "station code", "year", "month", "day", "init_ind", "init_time", "final_ind", "final_time", "peak_ind", 
           "peak_time", "location", "optical", "something", "xray_class", "xray_size", "station", "blank", "NOAA_AR", "etc"]

    widths=[2, 3, 2, 2, 2, 2, 4, 1, 4, 1, 4, 7, 3, 22, 1, 3, 8, 8, 6, 24]

    xray_df=pd.read_fwf(xray_file, widths=widths, header=None, names=names, parse_dates=[[2, 3, 4]])
    #translates dates to datetime
    xray_df["location"]=[x if str(x)[0]=="N" or str(x)[0]=="S" else None for x in xray_df["location"]]
    xray_df["init_date"]=create_datetime(xray_df["year_month_day"], xray_df["init_time"])
    xray_df["peak_date"]=create_datetime(xray_df["year_month_day"], xray_df["peak_time"])
    xray_df["final_date"]=create_datetime(xray_df["year_month_day"], xray_df["final_time"])

    xray_df=xray_df[["init_date", "peak_date", "final_date", "location", "xray_class", "xray_size", "NOAA_AR"]]
       
    ha_df="not yet implemented"
    return (xray_df, ha_df)

def get_flare_catalog(start_year=2013, stop_year=2014):

    try:
        print("downloading")
        (xray, halpha)=download_flare_catalog(start_year, stop_year)
    except:
        print("getting from file, years are only those downloaded")
        (xray, halpha)=get_flare_catalog_fromfile()
    return (xray, halpha)
                            
get_flare_catalog()

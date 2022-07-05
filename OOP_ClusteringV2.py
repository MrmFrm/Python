# OOP Clustering Code: H2 demand + el. demand + time series
# Include Time Series to the Clustering Algorithm


# OOP Tutorial for Python: https://www.youtube.com/watch?v=Ej_02ICOIgs
# Clustering Tutorial: https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/

# Import of packages needed for the code
import numpy as np # library adding support for large, multi-dimensional arrays and matrices
import os # to read (or write in) files
import csv # import to read csv files
import time

from classes import ClusteringData, ExcelSheet, RegionNuts3 # self implemented classes, see classes.py

# Measure runtime
startTime = time.time()

# Create Object of Class ExcelSheet to import the data
demandData = ExcelSheet('../data/web_nuts3_energietraeger.xlsx')
#demandData = ExcelSheet('../data/web_nuts3_energietraeger_minimiert.xlsx')
# Import the data of the excel table in demandData.data as a dataframe
demandData.importData()
# Access every single NUTS3 region via: demandData.allRegionsNuts3[1].excelRow
# Access of filtered NUTS3 regions (year, szenario) via: demandData.demandEl_list[0] or demandData.demandH2_list
executionTime = (time.time() - startTime)
print('Execution time to import demand Data in min: ' + str(executionTime/60))
# 0.185 Minutes
cluData1 = ClusteringData(demandData)
Z = cluData1.calculateCluster()
cluData1.plot(Z, type="dendogram")

# Measure runtime
startTime = time.time()

# Create Object of Class ExcelSheet to import the data
tsData_pvr = ExcelSheet('../data/EE-Knotenzeitreihen_pvr_37670.xlsx')
#tsData_pvr = ExcelSheet('../data/EE-TS_pvr_minimiert.xlsx')
# Import the data of the excel table in tsData_pvr.data as a dataframe
tsData_pvr.importData()
# Access every single NUTS3 region via: tsData_pvr.allRegionsNuts3[1].excelRow
executionTime = (time.time() - startTime)
print('Execution time to import time series Data in min: ' + str(executionTime/60))
# Private Laptop: 11.8 Minutes

# Create Object of Class ExcelSheet to import the data
tsData_wind = ExcelSheet('../data/EE-Knotenzeitreihen_windonshore_37670.xlsx')
#tsData_wind = ExcelSheet('../data/EE-TS_windonshore_minimiert.xlsx')
tsData_wind.importData()

# Create Object of Class ExcelSheet to import the data
tsData_sopv = ExcelSheet('../data/EE-Knotenzeitreihen_sopv_37670.xlsx')
#tsData_sopv = ExcelSheet('../data/EE-TS_sopv_minimiert.xlsx')
tsData_sopv.importData()





# Inputregions: 
input_list = [demandData, tsData_pvr, tsData_wind, tsData_sopv]
cluData2 = ClusteringData(input_list)
#TODO: Year=2050 input in importData verschieben, damit konsistent

# Calculate the Clustering
Z = cluData2.calculateCluster()

cluData2.plot(Z, type="dendogram")
cluData2.plot(Z, type="dendogram", criterion = 'distance', max_d = 100)

cluData2.plot(Z, type="dendo_truncated")
cluData2.plot(Z, type="dendo_truncated", criterion = 'maxclust', max_d = 100)

cluData2.plot(Z, type="dendo_fancy")
cluData2.plot(Z, type="dendo_fancy", criterion = 'maxclust', max_d = 100)



# TODO: Test, if only one Input (e.g. timeseries, only )
# TODO: Test, if two inputs!



        

print("debugging mode")



#TODO ausführliches Testen! ob Daten noch gleich sind wie vorher





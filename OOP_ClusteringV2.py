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
demandData = ExcelSheet('../data/ISI/web_nuts3_energietraeger.xlsx')
# Import the data of the excel table in demandData.data as a dataframe
demandData.importData()
# Access every single NUTS3 region via: demandData.allRegionsNuts3[1].excelRow
# Access of filtered NUTS3 regions (year, szenario) via: demandData.demandEl_list[0] or demandData.demandH2_list
executionTime = (time.time() - startTime)
print('Execution time to import demand Data in min: ' + str(executionTime/60))

# Measure runtime
startTime = time.time()

# Create Object of Class ExcelSheet to import the data
tsData_pvr = ExcelSheet('../data/ISI/EE-Knotenzeitreihen_pvr_37670.xlsx')
# Import the data of the excel table in tsData_pvr.data as a dataframe
tsData_pvr.importData()
# Access every single NUTS3 region via: tsData_pvr.allRegionsNuts3[1].excelRow
executionTime = (time.time() - startTime)
print('Execution time to import time series Data in min: ' + str(executionTime/60))




# Inputregions: 
input_list = [demandData.allRegionsNuts3, tsData_pvr.allRegionsNuts3]
cluData2 = ClusteringData(input_list)
#TODO: Year=2050 input in importData verschieben, damit konsistent

# Calculate the Clustering
Z = cluData2.calculateCluster()
cluData2.plot(Z, type="dendogram")
#TODO ob Daten noch gleich sind wie vorher





        

print("debugging mode")








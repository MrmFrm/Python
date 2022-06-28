# OOP Clustering Code: H2 demand + el. demand
# OOP Tutorial for Python: https://www.youtube.com/watch?v=Ej_02ICOIgs
# Clustering Tutorial: https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/

# Import of packages needed for the code
import numpy as np # library adding support for large, multi-dimensional arrays and matrices
import os # to read (or write in) files
import csv # import to read csv files
from classes import ClusteringData, ExcelSheet, RegionNuts3 # self implemented classes, see classes.py

# Create Object of Class ExcelSheet to import the data
demandData = ExcelSheet('../data/ISI/web_nuts3_energietraeger.xlsx')
# Import the data of the excel table in demandData.data as a dataframe
demandData.importData() # Default: year 2050, Szenario: H2
# Access every single NUTS3 region via: demandData.allRegionsNuts3[1].excelRow

# Creacte Object of Class ClusteringData to do the clustering.
cluData = ClusteringData(data = demandData)
# Attributes of this class
# Z.paths, Z.types_of_excel, Z.df_raw, Z.namesNuts3

# Calculate the Clustering 
Z = cluData.calculateCluster()


# Plot the Clustering in different ways
cluData.plot(Z, type="2D")
cluData.plot(Z, type="2D", criterion = 'distance', max_d = 7) # define maximum distance 
cluData.plot(Z, type="2D", criterion = 'maxclust',  k = 10) # define number of clusters

cluData.plot(Z, type="dendogram")
cluData.plot(Z, type="dendogram", criterion = 'distance', max_d = 5)

cluData.plot(Z, type="dendo_truncated")
cluData.plot(Z, type="dendo_truncated", criterion = 'maxclust', max_d = 7)

cluData.plot(Z, type="dendo_fancy")
cluData.plot(Z, type="dendo_fancy", criterion = 'maxclust', max_d = 7)



# TODO fehler beheben:
# das Setzen von timeSeries = True ohne einbinden von anderen Daten sollte zu keiner Änderung von df führen!
#cluData2 = ClusteringData(demandData.allRegionsNuts3, timeSeries = True, year = 2050, szenario = 'TN-H2-G')
#Z2 = cluData2.calculateCluster()
#cluData2.plot(Z, type="dendogram")
# Problem: Elec. Data nicht gleich! cluData2.df != cluData.df, + warum steht Elec. hier links?







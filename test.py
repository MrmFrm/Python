import numpy as np # library adding support for large, multi-dimensional arrays and matrices
import os # to read (or write in) files
import csv # import to read csv files
import time

from classes import ClusteringData, ExcelSheet, RegionNuts3 # self implemented classes, see classes.py


demandData = ExcelSheet('../data/web_nuts3_energietraeger.xlsx')
demandData.importData()
cluData1 = ClusteringData(demandData)
Z = cluData1.calculateCluster()
cluData1.plot(Z, type="dendogram")
print("")

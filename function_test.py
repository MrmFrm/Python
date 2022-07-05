from classes import ClusteringData, ExcelSheet, RegionNuts3

demandData = ExcelSheet('../data/web_nuts3_energietraeger.xlsx')
demandData.importData()

#def mergeSameRegions()



tsData_pvr = ExcelSheet('../data/EE-Knotenzeitreihen_pvr_37670.xlsx')
tsData_pvr.importData()

lst = [demandData, tsData_pvr]
print("")

#find common names in list
#for idx, element in enumerate(list):

#set = set(list[0])
#intersection =


n1 = demandData.getRegionNames()
n2 = tsData_pvr.getRegionNames()
commonNames = list(set(n1).intersection(n2))
commonNames.sort()


# welche Regionen in demandData sind nicht in time Series Excel
st = set(commonNames) # set(commonNames)
print([i for i, e in enumerate(n1) if e in st]) # schauen welche von self.df_raw.names (demand data) nicht  in common Names sind
print([i for i, e in enumerate(n2) if e in st]) # schauen welche von aktuellem Element (data.getRegionNames()) nicht  in common Names sind

# Index of regions that are in commonNames
#indx1 = [i for i, e in enumerate(n1) if e in st]
#indx2 = [i for i, e in enumerate(n2) if e in st]

# Keep those regions, drop the others
names_included = [e for e in n1 if e in st]
names_notIncl = [e for e in n1 if e not in st] # in damandData
print("TODO not included message, deleted")
#self.df_raw = ...
#demandData.demandEl_list

#for idx, element_excel in enumerate(lst):
    #if element_excel.type_of_excel == "demands":



testLst = lst.append(1)

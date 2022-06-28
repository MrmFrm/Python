# Minimalbeispiel Merge
from classes import ExcelSheet

# Create Object of Class ExcelSheet to import the data
demandData = ExcelSheet('../data/ISI/web_nuts3_energietraeger.xlsx')
# Import the data of the excel table in demandData.data as a dataframe
demandData.importData()

list_of_regions = demandData.allRegionsNuts3
 
resulting_list = [list_of_regions[0]]
for sub_list in list_of_regions[1:]:
    if sub_list != resulting_list[-1]:
        resulting_list.append(sub_list)

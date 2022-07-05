from sklearn.preprocessing import StandardScaler #py -m pip install sklearn
from sklearn import preprocessing
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

import os
import pandas as pd
import numpy as np

# TODO add Readme file mit links zum Wiki + sonstigen Tipps von Eidelloth Stefan
# TODO Ordnerstruktur wie von Stefan empfohlen ( src, test, ...)

# Class to load data from Excel file and to generate objects of class RegionNuts3 for each row
class ExcelSheet:
    # Class Attribute can be added here
    # List which includes all "ExcelSheet" objects, that are generated
    all = []
    # Constructor
    def __init__(self, path = '../data/web_nuts3_energietraeger.xlsx' ):
        # Validation of input
        assert os.path.exists(path), f"Path {path} does not exist"

        # Assign to self object, path is a read only object (can't be changed normally)
        self.__path = path
        self.allRegionsNuts3 = []


        # Actions to execute
        ExcelSheet.all.append(self) # append instance, that is generated to list named "all"
        #print(f"Creation of object of class {self.__class__.__name__} successful")
     

    @property
    # Property Decorator = Read-Only Attribute
    def path(self):
        return self.__path
    
    # If you still want to set the read-only Attribute
    @path.setter
    def path(self, value):
        # hier häufig noch eine Abfrage zur Encapsulation
        self.__path = value
    
    # Method that imports the data from the ExcelSheet and stores it in the attribute data as a dataframe
    def importData(self, year = 2050, szenario = 'TN-H2-G'):
        print("\n\nImport of data from excelsheet...")
        xls = pd.ExcelFile(self.path)
        sheets = xls.sheet_names # To get names of all the sheets
        self.year = year

        
        
        # Recognition of the file : demand or time series
        if(len(sheets) ==1):
            print("Excel with demand data detected")
            #TODO hier einen aufwändigeren Format-Check durchführen

            self.type_of_excel = "demands"
            self.data = pd.read_excel(self.path)
            self.szenario = szenario

            # Creation of RegionNuts3 object for every row of the excel file
            self.instantiate_nuts3()        

            # Creation of demand list for a desired year and szenario
            self.demandH2_list = []
            self.demandEl_list = []
            self.getDemands(self.allRegionsNuts3)

        
        if (len(sheets) == 6): # time series excel sheet
            print("Excel with time series detected")
            #TODO hier einen aufwändigeren Format-Check durchführen


            self.type_of_excel = "timeSeries"
            print("High data load: This might take some time (~4 min)")
            allData = pd.DataFrame()
            for idx, sheetname in enumerate(sheets):
                df = pd.read_excel(self.path, sheet_name=sheetname)
                if idx == 0:
                    allData = df
                else:
                    allData = pd.concat((allData,df.iloc[:,2:]), axis=1)

                print(f"...Sheet {idx+1} of 6 completed...")
            self.data = allData
            
            # Because of the high demand of data, instantiate nuts3 only for data for the desired year (e.g. 2050)
            self.instantiate_nuts3() 

            # Creation of time series list for a desired year and szenario
            self.ts_list = []

            # Check if another Excelfile was already imported
            if len(self.all) > 1:
                #read the regions that are in the other Excelsheet
                if self.all[0].type_of_excel == "demands":
                    self.getTS(list_NUTS3 = self.allRegionsNuts3, regions2Compare = self.getRegionNames(data=self.all[0].demandEl_list))
                    
                elif self.all[0].type_of_excel == "timeSeries":
                    #TODO
                    self.getTS(list_NUTS3 = self.allRegionsNuts3, regions2Compare = self.getRegionNames(data=self.all[0].ts_list))
                    
                else:
                    self.getTS(list_NUTS3= self.allRegionsNuts3)
            # TODO else: falls Ts excel als erstes eingelesen wurde, alle übernehmen und ggfs. bei 2. Einlesen demand namen daran anpassen


        #TODO mit shape[?] probieren
        print(f"Import and Creation of {len(self.data)} objects of class RegionNuts3 successful")



    # Function that iterates through the data of the Excel File and creates objects for each row (of demand file)/column (time series file)
    def instantiate_nuts3(self):
        # Check if the Excel file lists the energy demand ('../data/ISI/web_nuts3_energietraeger.xlsx')
        if sorted(self.data.columns.values) == sorted(['Region', 'Szenario', 'Energieträger', 'Value', 'Jahr', 'Sektor']):
            for index, row in self.data.iterrows():
                # TODO : Vereinheitlichen! Auch hier nur die für self.year verwenden!
                self.allRegionsNuts3.append(RegionNuts3(row))

        # Check if the Excel file is a time-series excel
        elif (self.data.columns[0] == 'year' and self.data.columns[1] == 'hour'):
            for col_name, col_data in self.data.iteritems():
                # instantiate regions with ts ONLY for the year 2050, otherwise it's computionally too expensive 
                if col_name != 'year' and col_name != 'hour':
                    if self.year == 2030:
                        self.allRegionsNuts3.append(RegionNuts3(col_data[0:(8759)]))
                    elif self.year == 2040:
                        self.allRegionsNuts3.append(RegionNuts3(col_data[8760:(8760+8759)]))
                    elif self.year == 2050:
                        self.allRegionsNuts3.append(RegionNuts3(col_data[17520:(17520+8760)]))
                    else:
                        print(f"Year {self.year} is not part of the excel file")
        else:
            print("Unknown format")

    def getDemands(self, list_NUTS3 = list):
    # Pick the list elements that represent the regions that should be clustered
        for x in list_NUTS3:
            if type(x) != RegionNuts3:
                print("Wrong input to getDemands!")
            else:

                if x.szenario == self.szenario and x.year == self.year:
                    #if self.demandH2 == True and x.carrier == 'H2'
                    if x.carrier == 'H2':
                        self.demandH2_list.append(x)
                    #if self.demandEl == True and x.carrier == 'Strom':
                    if x.carrier == 'Strom':
                        self.demandEl_list.append(x)
        # For every region, there should be only ONE H2 demand and only ONE Electicity demand
        self.merge2Regions()

        # Compare and unify regions of H2 demand and Elecricity demand:
        self.unifyReg()
    # This method puts together the values (demands) of two rows in the demand-Excel, if they are given for the same region
    # The demands of this regions are added
    # Reason: In the Excelsheet for H2 + Electricity demands, H2 has two entries for each region (sector: 1x Verkehr, 1x Andere)
    def merge2Regions(self):
        resulting_list = [self.demandH2_list[0]]
        for list_element in self.demandH2_list[1:]:
            #print(list_element.name)
            list_element.name = self.removeSpace(list_element.name)
            if list_element.name != resulting_list[-1].name:
                resulting_list.append(list_element)
            else:
                # two (or more) consecutive list elements describe the H2 demand for the same NUTS3 region
                # Update last value of the resulting list 
                resulting_list[-1].value = resulting_list[-1].value + list_element.value
                resulting_list[-1].sector = resulting_list[-1].sector + ' + ' + list_element.sector
                # Update these new values also in the dataframe property ("excelRow") of the resulting List
                resulting_list[-1].excelRow["Value"] = resulting_list[-1].value
                resulting_list[-1].excelRow["Sektor"] = resulting_list[-1].sector
       
        # print(f"resulting_list has {len(resulting_list)} elements") 
        self.demandH2_list = resulting_list
        if (len(self.demandH2_list) != len(self.demandEl_list)):
            print("Not the same amount of values for the H2/Electricity demands!")
        
    def unifyReg(self):
        resulting_list = []
        print("Unify the demand data to get the same amount of values ...")

        # put the demand list in the same order
        self.demandEl_list.sort(key=lambda e: e.name)
        self.demandH2_list.sort(key=lambda e: e.name)

        n0 = self.getRegionNames(data=self.demandEl_list)
        n1 = self.getRegionNames(data=self.demandH2_list)
        commonNames = list(set(n0).intersection(n1))
        commonNames.sort()

        arr = np.empty([len(commonNames), 2], dtype=object)

        for idx, elementH2 in enumerate(self.demandH2_list):
            if elementH2.name  not in commonNames:
                self.demandH2_list.pop(idx)
                print(f"    - region {elementH2.name} deleted, since no value of electricity demand was available for it.")


        for idx, element in enumerate(self.demandEl_list):
            if element.name not in commonNames:  # if its the same region at this index idx
                self.demandEl_list.pop(idx)
                print(f"    - region {element.name} deleted, since no value of H2 demand was available for it.")


        if (len(self.demandEl_list) == len(self.demandH2_list)):
            print("Demand data successfully unified ")
        else:
            print("Still inconsistancies in the demand data!")

        #if self.ts == True:
        #    ("TODO: unifyReg not yet implemented for timeseries!")


        #pass # TODO
    def getTS(self, list_NUTS3: list, regions2Compare = list()):
        # data is a list of RegionsNuts3
        # regions2Compare is a list of names
        for idx, element in enumerate(list_NUTS3):
            if type(element) != RegionNuts3:
                print("Wrong input to getTS!")
            else:
                if len(regions2Compare) == 0:
                    self.ts_list.append(element)
                else:
                    if element.name in regions2Compare:
                        self.ts_list.append(element)
                                
        self.ts_list.sort(key=lambda e: e.name)
    def removeSpace(self, string: str):
        return string.replace(" ", "")

    # Definition of the representation of instances of the class
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.path}')"
    
    @staticmethod # just an example
    def is_integer(num):
        # We will count out the floats that are point zero
        if isinstance(num, float):
            # Count out the gloats that are point zero
            return num.is_integer()
        elif isinstance(num, int):
            return True
        else:
            return False

    def getRegionNames(self, data = []):
        names = []
        if len(data) == 0:
            if self.type_of_excel == "demands":
                for element in self.demandEl_list:
                    names.append(element.name)
            elif self.type_of_excel == "timeSeries":
                for element in self.ts_list:
                    names.append(element.name)
        else:
            for element in data:
                if type(element) != RegionNuts3:
                    print("wrong input data to getRegionNames()")
                else:
                    names.append(element.name)
        return names

# Inheritance from class ExcelSheet which represents each NUTS3 region
class RegionNuts3(ExcelSheet):
    # Constructor of the class
    def __init__(self, row: pd.core.series.Series, path = '../data/web_nuts3_energietraeger.xlsx' ):
        # Call to super function to have access to all attributes / methods
        #super().__init__(
        #    path
        #)
        # Validation of input
        assert os.path.exists(path), f"Path {path} does not exist"

        # Assign to self object, path is a read only object (can't be changed normally)
        self.__path = path
        self.allRegionsNuts3 = [] # #TODO ! funktioniert das? Dasselbe Attribut in Parent-Class
        # Check input variables TODO

        # Set Attributes depending on input
        self.excelRow = row

        if len(row) == 8760:
            self.timeSeries = row
            self.name = row.name
        else:
            self.excelRow = row
            self.name = row["Region"]
            self.szenario = row["Szenario"]
            self.carrier = row["Energieträger"]
            self.value = row["Value"]
            self.year = row["Jahr"]
            self.sector = row["Sektor"]
        
        # Actions to execute


    # Method definition
    # Definition of the representation of instances of the class
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.excelRow}')"
    
# Class to perform and plot the clustering Algorithm
class ClusteringData():
    # Constructor of the class
    def __init__(self, data):
        # Input check # TODO!
        # lists_NUTS3 can either be ONE Excelsheet or a list of Excelsheets
        if type(data) == ExcelSheet:
            self.paths = data.path
            self.year = data.year
            self.types_of_excel = data.type_of_excel

            if data.type_of_excel == "demands":
                print("Clustering the demand of H2 and the demand of Electricity")
                self.szenario = data.szenario
                self.df_raw, self.namesNuts3 = self.builtDemandArr(data)

            
            elif data.type_of_excel == "timeSeries":
                print("Attention: Add another ExcelSheet to ClusteringData() to enable the clustering!") # TODO exit the function here: Dont create a ClusteringData Object

            
        elif type(data) == list:
            self.year = data[0].year 
            self.paths = []
            self.types_of_excel = []

            if type(data[0]) != ExcelSheet:
                print("Error: The input to Clustering Data has to be a list of ExcelSheet Objects!")
            elif  data[0].type_of_excel != "demands":
                print("Please load a demand file first")  # TODO: andere Reihenfolge evtl. noch implementieren
            else:
                #data[0] is demand file:
                self.paths.append(data[0].path)
                self.types_of_excel.append(data[0].type_of_excel)
                self.szenario = data[0].szenario
                self.df_raw, self.namesNuts3 = self.builtDemandArr(data[0])


                namesOfReg = []
                commonNames = self.namesNuts3 # Regions within demand excel file

                # complete attributes by remaining Excelsheet-Objects stored in data
                for idx, element in enumerate(data[1:]):# TODO check this loop when loading multiple files!
                    self.paths.append(element.path)
                    self.types_of_excel.append(element.type_of_excel)
                    self.add_region2Clu(element, self.namesNuts3)

                #self.namesNuts3 = commonNames
        else:
            print("Wrong input to ClusteringData")

        print(f"Creation of object of class {self.__class__.__name__} successful")

    # Method definition
    def completeRegions(self, data: ExcelSheet, names: list):
        if data.type_of_excel == "timeSeries":
            st = set(names)  # set(commonNames)
            # TODO das alles hier nur machen, wenn Regions inkonsistent (Abfrage einfügen)
            # identify regions, that are not in both Excelfiles
            names_notIncl1 = [e for e in self.namesNuts3 if e not in st]  # check in self.namesNuts 3, which contains all regions of the demand file, ONLY IN DEMAND FILE
            names_notIncl2 = [e for e in data.getRegionNames() if e not in st]  # check in data, which contains all regions of the second/third/... Excelfile, ONLY IN TS FILE

            # Keep those regions, drop the others
            for i in names_notIncl1:
                print(f"    - region {i} deleted, since this region is not included in all files.")
            for i in names_notIncl2:
                print(f"    - region {i} deleted, since no time series was available for it.")

            # Complete Regions that are included in all files with data from all files:
            #idx1 = [i for i, e in enumerate(self.namesNuts3) if e in st]
            arr1 = self.df_raw.loc[names] # update array with updated regions, commonNames TODO hier fehlermeldung bei wind Reg.229 sollte rausfallen

            #TODO funtionalität hier prüfen, wenn mehrere files geladen!, Funktionalität single file auch überprüfen
            # fill time series list
            # arr2 = np.empty([len(names),8760], dtype=object) # check this! shape[0]
            lst = []
            for idx, element in enumerate(data.ts_list):
                if data.ts_list[idx].name in st:
                    lst.append(data.ts_list[idx].timeSeries)
            self.df_raw = pd.concat((arr1, pd.DataFrame(lst)), axis = 1)
            self.namesNuts3 = names # update the commonNames


        else:
            print("Within ClusteringData.completeRegions() : Not implemented yet")

    def add_region2Clu(self, data: ExcelSheet, commonNames):
        if data.year != self.year:
            print("The year of interest is not the same in the ExcelSheets!")
        # Regions of this Excelfile
        n1 = data.getRegionNames()
        newNames = list(set(n1).intersection(commonNames))
        newNames.sort()

        # TODO add regions to self.arr : if commonNames ==
        self.completeRegions(data, newNames)

    def builtDemandArr(self, data):
        # find common names in h2 list and el. list
        n0 = data.getRegionNames(data=data.demandEl_list)
        n1 = data.getRegionNames(data=data.demandH2_list)
        commonNames = list(set(n0).intersection(n1))
        commonNames.sort()

        arr = np.empty([len(commonNames), 2], dtype=object)

        for idx, elementH2 in enumerate(data.demandH2_list):

            if elementH2.name in commonNames:
                # H2 demand in column 0, arr[row][column]
                arr[idx][0] = data.demandH2_list[idx].value

        for idx, element in enumerate(data.demandEl_list):
            if element.name in commonNames:  # if its the same region at this index idx

                # Electricity demand in column 1
                arr[idx][1] = data.demandEl_list[idx].value
                # print(f"row {idx}: [{arr[idx,:]}] ")


        return pd.DataFrame(arr, columns=["H2", "Elec."], index=commonNames), commonNames

    def all_equal(lst):
        return not lst or lst.count(lst[0]) == len(lst)

    def getCommonReg(self, data):

        for idx, element in enumerate(data):
            print("")

    def calculateCluster(self):
        # fill array with data
        #arr = [] # parameters to cluster are listed in the columns

        #if self.demandEl == True and self.demandH2 == True:
        #if type(self.types_of_excel) == str: # this means that only one file is loaded, otherwise this would be a list
            #arr = self.df_raw.to_numpy()

        #else:
            #TODO add for multiple files! If Abfrage kann raus
        arr = self.df_raw.to_numpy()

        

        # Standardize features by removing the mean and scaling to unit variance.
        scaler = StandardScaler()
        scaler.fit(arr)
        arr_scaled = scaler.transform(arr)
        self.df_scaled = pd.DataFrame(arr_scaled, index=self.namesNuts3)




        

        # TODO Other normalization necessary?
        # https://scikit-learn.org/stable/modules/preprocessing.html#standardization-or-mean-removal-and-variance-scaling

        # Generate the linkage matrix to perform Hierarchical Clustering            # The input y may be either a 1-D condensed distance matrix or a 2-D array of observation vectors.
        # 'ward' = Ward variance minimization algorithm, bottom-up
        Z = linkage(self.df_scaled, 'ward')
        # Z[0]: [idx1, idx2, dist, sample_count]

        return Z

         

        if self.ts:
            print("calculateCluster not yet implemented for TS")
            # TODO add column for time series to the array 
        else:
            print("calculateCluster not implemented yet for this inpute combination")

    def plot(self, clusteringData, criterion = 'null', max_d = 0, k = 0, type= "dendogram", truncated = 12, *args, **kwargs):
        # The year and the szenario are printed above each plot
        plt.figure()
        if "demands" in self.types_of_excel:
            plt.suptitle(f'year: {self.year}, szenario: {self.szenario}', fontsize = 5)
        else:
            plt.suptitle(f'year: {self.year}', fontsize = 5)
           
        # Input validation
        # TODO input "criterion" löschen
        if criterion == 'distance' and max_d <= 0:
            print("Choose a distance (max_d > 0) to plot the clustering")
        elif criterion == 'distance' and max_d > 0:
            clusters = fcluster(clusteringData, max_d, criterion = criterion)
        elif criterion == 'maxclust' and k <= 0:
            print("Choose a number of clusters (k > 0) to plot the clustering")
        elif criterion == 'maxclust' and k > 0:
            clusters = fcluster(clusteringData, k, criterion = criterion)
        elif criterion == "inconsistency":
            #TODO
            print("this is not implemented yet")
            pass
        elif criterion == 'null' and k == 0 and max_d == 0: 
            print("ClusteringData.plot function: no criterion specified to cut off the clustering")
        else:
            print("Unexpected input: check input of ClusteringData.plot")

        
        # plot the demand data in a normal 2D graph:      
        if type=="2D":

            if "demands" in self.types_of_excel:
                plt.title('Demand data of NUT3 regions in Germany')
                plt.xlabel('scaled demand of H2')
                plt.ylabel('scaled demand of Electricity')
                if (max_d == 0 and k == 0):
                    plt.scatter(self.df_scaled["H2"], self.df_scaled["Elec."])
                elif max_d > 0 or k > 0 :
                    if k > 0:
                        plt.figtext(0.5,0.01, f"number of clusters = {k}", ha="center", va="center", fontsize=8)
                    else:
                        n = max(clusters) # number of cluster
                        plt.figtext(0.5,0.01, f"maximal distance = {max_d}, resulting number of clusters = {n} ", ha="center", va="center", fontsize=8)

                    plt.scatter(self.df_scaled["H2"], self.df_scaled["Elec."], c=clusters, cmap='prism')  # plot points with cluster dependent colors
                    plt.savefig("test_savefig.jpg")
                else: 
                    print ("Check input of the clusteringData.plot function")
        elif type == "dendogram":
            # calculate full dendrogram
            plt.title('Hierarchical Clustering Dendrogram')
            plt.xlabel('sample index')
            plt.ylabel('distance')
             
            dendrogram(
                clusteringData,
                leaf_rotation=90.,  # rotates the x axis labels
                leaf_font_size=8.,  # font size for the x axis labels
                labels=self.df_scaled.index, 
            )
            if max_d:
                plt.axhline(y=max_d, c='k')
        elif type =="dendo_truncated":
            plt.title('Hierarchical Clustering Dendrogram (truncated)')
            plt.xlabel('sample index')
            plt.ylabel('distance')
            dendrogram(
                clusteringData,
                truncate_mode ='lastp',  # show only the last p merged clusters
                p = truncated,  # show only the last p merged clusters
                show_leaf_counts = False,  # otherwise numbers in brackets are counts
                leaf_rotation = 90.,
                leaf_font_size = 10.,
                show_contracted = True,  # to get a distribution impression in truncated branches
                labels=self.df_scaled.index,

                #show_leaf_counts=False
            )
            if max_d:
                plt.axhline(y=max_d, c='k')
        elif type == "dendo_fancy":
            if max_d == 0:
                self.fancy_dendogram(
                    clusteringData,
                    truncate_mode='lastp',
                    p=12,
                    leaf_rotation=90.,
                    leaf_font_size=10.,
                    show_contracted=True,
                    annotate_above=10,  # useful in small plots so annotations don't overlap
                    labels=self.df_scaled.index,

                )
            else:
                self.fancy_dendogram(
                    clusteringData,
                    max_d = max_d,
                    truncate_mode='lastp',
                    p=12,
                    leaf_rotation=90.,
                    leaf_font_size=10.,
                    show_contracted=True,
                    annotate_above=10,  # useful in small plots so annotations don't overlap
                    labels=self.df_scaled.index,

                )
        #plt.show(block=False)
        #plt.show()
        plt.savefig(f"Clustering_{type}.jpg")

    def fancy_dendogram(self, *args, **kwargs):
            max_d = kwargs.pop('max_d', None)
            if max_d and 'color_threshold' not in kwargs:
                kwargs['color_threshold'] = max_d
            annotate_above = kwargs.pop('annotate_above', 0)

            ddata = dendrogram(*args, **kwargs)

            if not kwargs.get('no_plot', False):
                plt.title('Hierarchical Clustering Dendrogram (fancy)')
                plt.xlabel('sample index or (cluster size)')
                plt.ylabel('distance')
                for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
                    x = 0.5 * sum(i[1:3])
                    y = d[1]
                    if y > annotate_above:
                        plt.plot(x, y, 'o', c=c)
                        plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                        textcoords='offset points',
                        va='top', ha='center')
                if max_d:
                        plt.axhline(y=max_d, c='k')
            return ddata       

        
        
    #def indices(mylist, value):
    #    return [i for i,x in enumerate(mylist) if x==value]
    #
    # 



     

    def exportCluster(self):
        #TODO!
        pass
        

    


from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

import os
import pandas as pd
import numpy as np


# Class to load data from Excel file and to generate objects of class RegionNuts3 for each row
class ExcelSheet:
    # Class Attribute can be added here
    # List which includes all "ExcelSheet" objects, that are generated
    all = []
    # Constructor
    def __init__(self, path = '../data/ISI/web_nuts3_energietraeger.xlsx' ):
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
            self.type_of_excel = "timeSeries"
            print("High data load: This might take some time")
            #cols = 0
            allData = pd.DataFrame()
            for idx, sheetname in enumerate(sheets):
                df = pd.read_excel(self.path, sheet_name=sheetname)
                #cols += df.shape[1]
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
                    self.getTS(list_NUTS3.allRegionsNuts3)



        #TODO mit shape[?] probieren
        print(f"Import and Creation of {len(self.data)} objects of class RegionNuts3 successful")



    # Function that iterates through the data of the Excel File and creates objects for each row (of demand file)/column (time series file)
    def instantiate_nuts3(self):
        # Check if the Excel file lists the energy demand ('../data/ISI/web_nuts3_energietraeger.xlsx')
        if sorted(self.data.columns.values) == sorted(['Region', 'Szenario', 'Energieträger', 'Value', 'Jahr', 'Sektor']):
            print("Excel with demand data detected")
            for index, row in self.data.iterrows():
                # TODO : Vereinheitlichen! Auch hier nur die für self.year verwenden!
                self.allRegionsNuts3.append(RegionNuts3(row))

        
        elif (self.data.columns[0] == 'year' and self.data.columns[1] == 'hour'):
            print("Excel with time series detected")
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

        notIncluded = 0
        for indexH2, elementH2 in enumerate(self.demandH2_list): 
            for indexEl, elementEl in enumerate(self.demandEl_list):
                notIncluded = notIncluded + int(elementH2.name != elementEl.name)
              
            if (notIncluded == len(self.demandEl_list)):
                self.demandH2_list.pop(indexH2)
                print(f"    - region {elementH2.name} deleted, since no value of electricity demand was available for it.")
              
            notIncluded = 0

        #put the demand list in the same order
        self.demandEl_list.sort(key=lambda e: e.name)
        self.demandH2_list.sort(key=lambda e: e.name)

            
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

    def getRegionNames(self, data: list):
        names = []
        for idx, element in enumerate(data):
            if type(element) != RegionNuts3:
                print("wrong input data to getRegionNames! (Has to be list of RegionNuts3")
            else:
                names.append(element.name)
        return names

# Inheritance from class ExcelSheet which represents each NUTS3 region
class RegionNuts3(ExcelSheet):
    # Constructor of the class
    def __init__(self, row: pd.core.series.Series, path = '../data/ISI/web_nuts3_energietraeger.xlsx' ):
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
        self.year = data.year
        if type(data) == ExcelSheet:
            self.paths = data.path
            self.types_of_excel = data.type_of_excel
            if data.type_of_excel == "demands":
                print("Clustering the demand of H2 and the demand of Electricity")
                self.szenario = data.szenario

                # Check if lists are sorted in the same way
                names = []
                arr = np.empty([len(data.demandEl_list),2], dtype = object)
            
                for idx, element in enumerate(data.demandEl_list):
                    if element.name == data.demandH2_list[idx].name: # if its the same region at this index idx
                        names.append(element.name)
                        # H2 demand in column 0, arr[row][column]
                        arr[idx][0] = data.demandH2_list[idx].value
                        # Electricity demand in column 1
                        arr[idx][1] = data.demandEl_list[idx].value
                        # print(f"row {idx}: [{arr[idx,:]}] ")
                    else: 
                        print("The demand data of H2 and Electricity is not in the same order")
                self.df_raw = pd.DataFrame(arr, columns=["H2", "Elec."], index=names)
                self.namesNuts3 = names
            
            elif data.type_of_excel == "timeSeries":
                print("Attention: Add another ExcelSheet to enable the clustering!")
            
        elif type(data) == list:
            for idx, element in enumerate(data):
                if type(element) != ExcelSheet:
                    print("Error: The input to Clustering Data has to be a list of ExcelSheet Objects!")
                else:
                    self.paths.append(element.path)
                    self.types_of_excel.append(element.type_of_excel)
                    # TODO: compare regions of ExcelSheets and adapt them
        else:
            print("Wrong input to ClusteringData")


       

            


            
        #elif all(isinstance(elem, RegionNuts3) for elem in lists_NUTS3):
            # This checks, if only one list is given --> I
            # e.g. this is the case, if only the demand data should be clustered
            # if list of demands
                #if len(list_element.excelRow) != 8760:# if excelfile.?.type=="demand"


                    

                    # Actions to execute when an object of this class is created
                    # Fill lists that should be used for the clustering
                    #if demandH2 == True or demandEl == True:
                    #self.getDemands(list_element)
                #else:
                    #if timeSeries == True:
                    #print("function for timeseries not implemented yet")
                    #self.ts_list = []
                    #self.getTS(list_element)

        #for idx, list_element in enumerate(lists_NUTS3):
        #    #TODO Input check 

        #    if type(list_element) != list:
        #        print("The input data for ClusteringData has to be a list of lists (of RegionNuts3 Objects)")
        #    elif type(list_element) == RegionNuts3:
        #        print("The input data for ClusteringData is a list of RegionsNuts3")

                

        print(f"Creation of object of class {self.__class__.__name__} successful")
    

    # Method definition

    def calculateCluster(self):
        # fill array with data
        arr = [] # parameters to cluster are listed in the columns

        #if self.demandEl == True and self.demandH2 == True:
        if type(self.types_of_excel) == str: # this means that only one file is loaded, otherwise this would be a list
            arr = self.df_raw.to_numpy()

        else:
            #TODO add for multiple files!
            pass

        

        # Standardize features by removing the mean and scaling to unit variance.
        scaler = StandardScaler()
        scaler.fit(arr)
        arr_scaled = scaler.transform(arr)

        self.df_scaled = pd.DataFrame(arr_scaled, columns=["H2", "Elec."], index=self.namesNuts3)

        

        # TODO Other normalization necessary?
        # https://scikit-learn.org/stable/modules/preprocessing.html#standardization-or-mean-removal-and-variance-scaling

        # Generate the linkage matrix to perform Hierarchical Clustering            # The input y may be either a 1-D condensed distance matrix or a 2-D array of observation vectors.
        # 'ward' = Ward variance minimization algorithm, bottom-up
        Z = linkage(arr_scaled, 'ward')
        # Z[0]: [idx1, idx2, dist, sample_count]

        return Z

         

        if self.ts:
            print("calculateCluster not yet implemented for TS")
            # TODO add column for time series to the array 
        else:
            print("calculateCluster not implemented yet for this inpute combination")

              
        
        
    def plot(self, clusteringData, criterion = 'null', max_d = 0, k = 0, type= "dendogram", truncated = 12,*args, **kwargs):
        # The year and the szenario are printed above each plot
        plt.figure()
        if "demands" in self.types_of_excel:
            plt.suptitle(f'year: {self.year}, szenario: {self.szenario}', fontsize = 5)
        else:
            plt.suptitle(f'year: {self.year}', fontsize = 5)
           
        # Input validation
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
                leaf_font_size=5.,  # font size for the x axis labels
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
                leaf_font_size = 12.,
                show_contracted = True,  # to get a distribution impression in truncated branches
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
                    leaf_font_size=12.,
                    show_contracted=True,
                    annotate_above=10,  # useful in small plots so annotations don't overlap
                )
            else:
                self.fancy_dendogram(
                    clusteringData,
                    max_d = max_d,
                    truncate_mode='lastp',
                    p=12,
                    leaf_rotation=90.,
                    leaf_font_size=12.,
                    show_contracted=True,
                    annotate_above=10,  # useful in small plots so annotations don't overlap
                )
        plt.show(block=False)   
                       

        


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
        pass
        

    


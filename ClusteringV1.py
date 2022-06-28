# Wasserstoff Nachfrage 2050
# Stromnachfrage 2050
import numpy as np
import pandas as pd # mächtige Erweiterung von numpy zur Datenverarbeitung


#item1 = Item()
#item1.name= "Phone"

#Klasse schreiben
#Attribute der Klasse
#Funktionen der Klasse, z.B. Excel einlesen
def getDemands():
    #form von data ist ein data.frame, welches quasi wie eine Exceldatei ist
    data = pd.read_excel('../data/ISI/web_nuts3_energietraeger.xlsx')
    h2Szenario = data[data["Szenario"]=="TN-H2-G"]
    h2Szenario2050 = h2Szenario[h2Szenario["Jahr"]==2050]
    demandH2 = h2Szenario2050[h2Szenario2050["Energieträger"]=="H2"]
    # wenn mehrere H2 Nachfragen für einen Landkreis gegeben sind, zusammenaddieren
    
    for i in demandH2["Region"]:
        for lineIdx in range(0, len(demandH2)):
            print(lineIdx)
            print(i)
            if all(i == demandH2["Region"].iloc[[lineIdx+1]]):
                print('-----IF-----')
                print("i = " + i )
                print("lineIdx = " + lineIdx)

                print('-----End IF -------')

        #lineIdx = lineIdx + 1

    

    demandElectr = h2Szenario2050[h2Szenario2050["Energieträger"]=="Strom"]
    print("data of demands completed")
    print("getDemands() completed")
    return(demandH2, demandElectr)

demands = getDemands() # type touple mit demand[0] = df(demandH2)
#print(demands)

#normalize data
demandH2_norm = demands[0]["Value"]/max(demands[0]["Value"])
demandElectr_norm = demands[1]["Value"] / max(demands[1]["Value"])


X = np.concatenate((demandH2_norm.to_numpy(), demandElectr_norm.to_numpy()))
print(X.shape)  # 150 samples with 2 dimensions 
plt.scatter(X[:,0], X[:,1])
plt.show()



## Use of the clustering function on vRES Generation Potentials from http://opendata.ffe.de/dataset/vres-generation-potentials-europe-nuts-3/


import json
#dataTest = json.load(open('..\Daten\\v_opendata_Res_Potential.json','r')) warum funktioniert das so nicht?


resPotential = '''
[{"id_opendata":50,"title":"vRES Generation Potentials (Europe NUTS-3)","oep_metadata":{"name": "id_opendata=50",
    "title": "vRES Generation Potentials (Europe NUTS-3)",
    "description": "Energy Generation potentials of variable renewable energy sources in Europe on NUTS-3-level",
    "language": ["en-GB", "en-US", "de-DE"],
    "keywords": ["wind-onshore", "pv"],
    "publicationDate": ["2020-11-30"],
    "context":
    {"homepage": "https://www.ffe.de/xos",
        "documentation": "http://opendata.ffe.de/dataset/vres-generation-potentials-europe-nuts-3/",
        "sourceCode": null,
        "contact": "https://www.ffe.de/die-ffe/die-personen/mitarbeiter-ffe/85",
        "grantNo": "03ET4062A",
        "fundingAgency": "Bundesministerium für Wirtschaft und Energie",
        "fundingAgencyLogo": "http://opendata.ffe.de/wp-content/uploads/2019/09/titel_foerderlogo_bmwi.jpg",
        "publisherLogo": "https://www.ffe.de/templates/ffe_v3/img/ffe_logo_2019.png"},
    "spatial":
    {"location": "europe",
        "extent": "europe",
        "resolution": "NUTS-3"},
    "temporal":
    {"referenceDate": null,
        "timeseries": null
    },
    "sources": [],
    "licenses": [
        {"name": "CC-BY-4.0",
            "title": "Creative Commons Attribution 4.0 International",
            "path": "https://creativecommons.org/licenses/by/4.0/legalcode",
            "instruction": "https://tldrlegal.com/license/creative-commons-attribution-4.0-international-(cc-by-4)",
            "attribution": "© FfE, eXtremOS Project"} ],
    "contributors": null,
    "resources": [
        {"profile": "tabular-data-resource",
            "name": "opendata.opendata",
            "path": "http://opendata.ffe.de:3000/opendata?id_opendata=eq.50",
            "format": "PostgreSQL",
            "encoding" : "UTF-8",
            "schema": {
                "fields": [
                    {"name": "id", "description": "Unique identifier", "type": "serial", "unit": null},
                    {"name": "id_opendata", "description": "Dataset identifier", "type": "integer", "unit": null},
                    {"name": "id_region_type", "description": "Region type identifier", "type": "integer", "unit": null},
                    {"name": "region_type", "description": "Region type name", "type": "text", "unit": null},
                    {"name": "id_region", "description": "Region identifer", "type": "integer", "unit": null},
                    {"name": "region", "description": "Region name", "type": "text", "unit": null},
                    {"name": "year", "description": "Simulation year", "type": "integer", "unit": null},
                    {"name": "year_weather", "description": "Weather year", "type": "integer", "unit": null},
                    {"name": "internal_id_type", "description": null, "type": "internal_id_type[1] = 16: Energy Carrier", "unit": null},
                    {"name": "internal_id", "description": null, "type": "internal_id[1] = 1: wind-onshore | 76: Freestanding PV | 75: PV on buildings", "unit": null},
                    {"name": "value", "description": "Value", "type": "double precision", "unit": "GWh"},
                    {"name": "values", "description": null, "type": null, "unit": null},
                    {"name": "geom", "description": "(Generalized) Geometry", "type": "geometry", "unit": "null"} ],
                "foreignKeys": [
                    {"fields": ["id_region_type"],
                        "reference": {
                            "resource": "opendata.region_description",
                            "fields": ["id_region_type"] }
                    },
                    {"fields": ["id_region_type", "id_region"],
                        "reference": {
                            "resource": "opendata.region",
                            "fields": ["id_region_type", "id_region"] }
                    }
                ] },
            "dialect": null } ],
    "review": null,
    "metaMetadata":
    {"metadataVersion": "OEP-1.4.0",
        "metadataLicense":
        {"name": "CC0-1.0",
            "title": "Creative Commons Zero v1.0 Universal",
            "path": "https://creativecommons.org/publicdomain/zero/1.0/"}
    },
    "_comment":
    {"metadata": "Metadata documentation and explanation (https://github.com/OpenEnergyPlatform/organisation/wiki/metadata)",
        "dates": "Dates and time must follow the ISO8601 including time zone (YYYY-MM-DD or YYYY-MM-DDThh:mm:ss±hh)",
        "units": "Use a space between numbers and units (100 m)",
        "languages": "Languages must follow the IETF (BCP47) format (en-GB, en-US, de-DE)",
        "licenses": "License name must follow the SPDX License List (https://spdx.org/licenses/)",
        "review": "Following the OEP Data Review (https://github.com/OpenEnergyPlatform/data-preprocessing/wiki)",
        "null": "If not applicable use (null)"}
'''

dataJson =json.loads(resPotential)
print(type(dataJson)) #list, data[0] = dict
print(len(dataJson)) #1
print(dataJson) 

keys = dataJson[0].keys()
values = dataJson[0].values() # values: class dict_values der Form
#....{'id_opendata': 50, 'id_region_type': 38, 'region_type': 'NUTS-3', 'id_region': 82600153, 'region': 'North Hampshire', 'year': 2012, 'year_weather': 2012, 'internal_id': [1], 'internal_id_1': 1, 'internal_id_2': None, 'internal_id_3': None, 'internal_id_4': None, 'value': 5082.51162220518, 'values': None}]])

print(len(keys)) # 5
print(len(values)) # 5
print(dataJson[0].keys()) #dict_keys(['id_opendata', 'title', 'oep_metadata', 'metadata_ffe', 'data'])


# Auf values zugreifen, indem man in eine Liste umwandelt
valueList = list(values)

#todo: von data[0] --> function variables, vRes Generation Potential, ID, Deutschland raussuchen und in kleinere Liste (?) schreiben fürs Clustering

#http://opendata.ffe.de/eem2019/
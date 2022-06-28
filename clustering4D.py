# Clustering 4 variables: https://stackoverflow.com/questions/38080769/multidimensional-hierarchical-clustering-python

# You can use the following code to display and store Matplotlib plots within a Python Jupyter notebook:
# %matplotlib inline
import matplotlib.pylab as plt
# Seaborn is a library for making statistical graphics in Python. It builds on top of matplotlib and integrates closely with pandas data structures.
import seaborn as sns 
# pandas is a Python package providing fast, flexible, and expressive data structures designed to make working with “relational” or “labeled” data both easy and intuitive. 
import pandas as pd
# NumPy is the fundamental package for scientific computing in Python. It is a Python library that provides a multidimensional array object, various derived objects,...
import numpy as np 

# pd.DataFrame = Two-dimensional, size-mutable, potentially heterogeneous 
# tabular data.
# Data structure also contains labeled axes (rows and columns). 
# Arithmetic operations align on both row and column labels. 
# Can be thought of as a dict-like container for Series objects. 
# The primary pandas data structure.
df = pd.DataFrame({"col" + str(num): np.random.randn(50) for num in range(1,5)})
#sns.clustermap uses scipy.cluster.hierarchy.linkage() as a method
sns.clustermap(df)
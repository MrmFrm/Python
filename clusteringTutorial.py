# Tutorial zum Clustering (Empfehlung Anna, Quelle: https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/)
# import necessary librarys
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np

# generate two clusters: a with 100 points, b with 50:
np.random.seed(4711)  # for repeatability of this tutorial (um Seed für den Pseudo-Zufallszahlengenerator-Algorithmus in Python zu setzen)
# Draw random samples from a multivariate normal distribution
a = np.random.multivariate_normal([10, 0], [[3, 1], [1, 4]], size=[100,]) #NV um [10,0], shape (100,2)
b = np.random.multivariate_normal([0, 20], [[3, 1], [1, 4]], size=[50,]) #shape (50,2)
# join a and b along axis 0: Hintereinanderreihen von a und b
X = np.concatenate((a, b),)
print(X.shape)  # 150 samples with 2 dimensions
plt.scatter(X[:,0], X[:,1])
plt.show() #unten rechts: a, oben links: b

# generate the linkage matrix to perform Hierarchical Clustering
# The input y may be either a 1-D condensed distance matrix or a 2-D array of observation vectors.
# 'ward' = Ward variance minimization algorithm, bottom-up
Z = linkage(X, 'ward')

from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist

# cophenet: compares pairwise distances of all your samples  to those implied in the hierarchical clustering (Z).
# the closer the value of c is to one, the better the clustering is
c, coph_dists = cophenet(Z, pdist(X))
c #0.9800148

#Z[i] shows which clusters were merged in the i-th iteration
Z[0] # first merge: original samples with indices 52 and 53 merged,their distance = 0.04151)
Z[1] # second merge
Z[:20] # first 20 iterations


#analyse iteration 14, 3. merge (33 und 68) an Stelle idx 152 gemerged
X[[33, 68, 62]]

idxs = [33, 68, 62]
plt.figure(figsize=(10, 8))
plt.scatter(X[:,0], X[:,1])  # plot all points
plt.scatter(X[idxs,0], X[idxs,1], c='r')  # plot interesting points in red again
plt.show() # we can see: points are quite close


idxs = [33, 68, 62]
plt.figure(figsize=(10, 8))
plt.scatter(X[:,0], X[:,1]) # plot all points
plt.scatter(X[idxs,0], X[idxs,1], c='r')
idxs = [15, 69, 41]
plt.scatter(X[idxs,0], X[idxs,1], c='y')
plt.show() # again: points quite close


# Way to plot hierarchical Clustering: DENDROGRAM
# Visualization in form of a tree showing the order and distances of merges during the hierarchical clustering
# calculate full dendrogram
plt.figure(figsize=(25, 10))
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('sample index')
plt.ylabel('distance')
dendrogram(
    Z,
    leaf_rotation=90.,  # rotates the x axis labels
    leaf_font_size=8.,  # font size for the x axis labels
)
plt.show()

#distances of the last 4 merges
Z[-4:,2] # out: array([ 15.11533118,  17.11527362,  23.12198936, 180.27043021])
# --> quite big distance in the last merge, indicating, that there are maybe at least 2 clusters

# Dendogram Truncation
plt.title('Hierarchical Clustering Dendrogram (truncated)')
plt.xlabel('sample index')
plt.ylabel('distance')
dendrogram(
    Z,
    truncate_mode='lastp',  # show only the last p merged clusters
    p=12,  # show only the last p merged clusters
    show_leaf_counts=False,  # otherwise numbers in brackets are counts
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,  # to get a distribution impression in truncated branches,
    #black dots at the heights of those previous cluster merges, heights small compared to the last merge
)
plt.show()# truncated dendrogram, which only shows the las p=12 out of 149 merges

# but: Most labels are missing in the truncated dendrogram
plt.title('Hierarchical Clustering Dendrogram (truncated)')
plt.xlabel('sample index or (cluster size)')
plt.ylabel('distance')
dendrogram(
    Z,
    truncate_mode='lastp',  # show only the last p merged clusters
    p=12,  # show only the last p merged clusters
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,  # to get a distribution impression in truncated branches
)
plt.show()


# Eye candy: Annotating the distances inside the dendrogram
def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
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


    fancy_dendrogram(
    Z,
    truncate_mode='lastp',
    p=12,
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,
    annotate_above=10,  # useful in small plots so annotations don't overlap
)
plt.show()


# Selecting a Distance Cut-Off aka Determining the Number of Clusters
# Basically we are interested in a huge jump in distance to find max_d
# e.g. set cut-off to 50
max_d = 50  # max_d as in max_distance

fancy_dendrogram(
    Z,
    truncate_mode='lastp',
    p=12,
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,
    annotate_above=10,
    max_d=max_d,  # plot a horizontal cut-off line
)
plt.show()

fancy_dendrogram(
    Z,
    truncate_mode='lastp',
    p=12,
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,
    annotate_above=10,
    max_d=16,
)
plt.show()


# Automated Cut-Off Selection (or why you shouldn't rely on this)
# Wikipedia lists a couple of common methods in ("Determining the number of clusters in a data set")
from scipy.cluster.hierarchy import inconsistent

depth = 5
incons = inconsistent(Z, depth)
incons[-10:]

depth = 3
incons = inconsistent(Z, depth)
incons[-10:]


# Elbow Method --> tries to find the clustering step where the acceleration 
# of distance growth is the biggest
last = Z[-10:, 2]
last_rev = last[::-1]
idxs = np.arange(1, len(last) + 1)
plt.plot(idxs, last_rev)

acceleration = np.diff(last, 2)  # 2nd derivative of the distances
acceleration_rev = acceleration[::-1]
plt.plot(idxs[:-2] + 1, acceleration_rev)
plt.show()
k = acceleration_rev.argmax() + 2  # if idx 0 is the max of this we want 2 clusters
print("clusters:", k)

# Example that the elbow method doesn't always work that well
c = np.random.multivariate_normal([40, 40], [[20, 1], [1, 30]], size=[200,])
d = np.random.multivariate_normal([80, 80], [[30, 1], [1, 30]], size=[200,])
e = np.random.multivariate_normal([0, 100], [[100, 1], [1, 100]], size=[200,])
X2 = np.concatenate((X, c, d, e),)
plt.scatter(X2[:,0], X2[:,1])
plt.show()



Z2 = linkage(X2, 'ward')
plt.figure(figsize=(10,10))
fancy_dendrogram(
    Z2,
    truncate_mode='lastp',
    p=30,
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,
    annotate_above=40,
    max_d=170,
)
plt.show() # maximum: 4 clusters

last = Z2[-10:, 2]
last_rev = last[::-1]
idxs = np.arange(1, len(last) + 1)
plt.plot(idxs, last_rev)

acceleration = np.diff(last, 2)  # 2nd derivative of the distances
acceleration_rev = acceleration[::-1]
plt.plot(idxs[:-2] + 1, acceleration_rev)
plt.show()
k = acceleration_rev.argmax() + 2  # if idx 0 is the max of this we want 2 clusters
print("clusters:", k)

print(inconsistent(Z2, 5)[-10:])

# Retrieve the Clusters
# Knowing max_d from dendrogram
from scipy.cluster.hierarchy import fcluster
max_d = 50
clusters = fcluster(Z, max_d, criterion='distance')
clusters

# or knowing k from dendrogram
k=2
fcluster(Z, k, criterion='maxclust')


#Using the Inconsistencs Method
from scipy.cluster.hierarchy import fcluster
fcluster(Z, 8, depth=10)


#Visualizing the clusters
plt.figure(figsize=(10, 8))
plt.scatter(X[:,0], X[:,1], c=clusters, cmap='prism')  # plot points with cluster dependent colors
plt.show()




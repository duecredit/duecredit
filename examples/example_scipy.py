import duecredit
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import pdist
from sklearn.datasets import make_blobs

data, true_label = make_blobs()

dist = pdist(data, metric='euclidean')

Z = linkage(dist, method='single')
# exercise 3.2.1

import pylab as pl
from scipy.io import loadmat
from similarity import similarity

# Image to use as query
i = 1

# Similarity: 'SMC', 'Jaccard', 'ExtendedJaccard', 'Cosine', 'Correlation'
similarity_measures = ['SMC', 'Jaccard', 'ExtendedJaccard', 'Cosine', 'Correlation']
similarity_measure = similarity_measures[0]

# Load the CBCL face database
# Load Matlab data file to python dict structure
X = loadmat('../data/wildfaces_grayscale.mat')['X']

N, M = X.shape


# Search the face database for similar faces
# Index of all other images than i
not_i = [n for n in range(N) if n != i]
# Compute similarity between image i and all others
sim = similarity(X[i, :], X[not_i, :], similarity_measure)
sim = sim.tolist()[0]
# Tuples of sorted similarities and their indices
sim_to_index = sorted(zip(sim, not_i))


# Visualize query image and 5 most/least similar images
pl.figure(figsize=(12, 8))
pl.subplot(3, 1, 1)
pl.imshow(pl.np.reshape(X[i], (40, 40)).T, cmap=pl.cm.gray)
pl.xticks([])
pl.yticks([])
pl.title('Query image')
pl.ylabel('image #{0}'.format(i))


for ms in range(5):

    # 5 most similar images found
    pl.subplot(3, 5, 6+ms)
    im_id = sim_to_index[-ms-1][1]
    im_sim = sim_to_index[-ms-1][0]
    pl.imshow(pl.np.reshape(X[im_id], (40, 40)).T, cmap=pl.cm.gray)
    pl.xlabel('sim={0:.3f}'.format(im_sim))
    pl.ylabel('image #{0}'.format(im_id))
    pl.xticks([])
    pl.yticks([])
    if ms == 2:
        pl.title('Most similar images')

    # 5 least similar images found
    pl.subplot(3, 5, 11+ms)
    im_id = sim_to_index[ms][1]
    im_sim = sim_to_index[ms][0]
    pl.imshow(pl.np.reshape(X[im_id], (40, 40)).T, cmap=pl.cm.gray)
    pl.xlabel('sim={0:.3f}'.format(im_sim))
    pl.ylabel('image #{0}'.format(im_id))
    pl.xticks([])
    pl.yticks([])
    if ms == 2:
        pl.title('Least similar images')
    
pl.show()

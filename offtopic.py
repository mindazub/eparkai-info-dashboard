import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.neighbors import KernelDensity

# Load the iris dataset from scikit-learn
iris = datasets.load_iris()
data = iris.data

# Create a grid of points over which to evaluate the density
x = np.linspace(data[:, 0].min(), data[:, 0].max(), 100)
y = np.linspace(data[:, 1].min(), data[:, 1].max(), 100)
X, Y = np.meshgrid(x, y)
xy_sample = np.vstack([X.ravel(), Y.ravel()]).T

# Fit the Kernel Density model on the first two features of the iris dataset
kde = KernelDensity(bandwidth=0.5)
kde.fit(data[:, :2])

# Evaluate the density model on the grid
Z = np.exp(kde.score_samples(xy_sample))
Z = Z.reshape(X.shape)

# Plot the density
plt.contourf(X, Y, Z, levels=20, cmap='viridis')
plt.scatter(data[:, 0], data[:, 1], s=10, c='red', edgecolor='k')
plt.title("Kernel Density Estimation of Iris Dataset")
plt.xlabel(iris.feature_names[0])
plt.ylabel(iris.feature_names[1])
plt.show()

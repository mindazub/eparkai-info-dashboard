import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets

# Define the mean, standard deviation, and number of samples
mean = 5.0
std = 0.5
N = 1000

# Generate random samples from a normal distribution
np.random.seed(10**7)
x = np.random.normal(mean, std, N)
   
num_bins = 50
   
# Plot the histogram
n, bins, patches = plt.hist(x, num_bins, 
                            density=True, 
                            color='green',
                            alpha=0.7)
   
# Plot the normal distribution curve
y = ((1 / (np.sqrt(2 * np.pi) * std)) *
     np.exp(-0.5 * ((bins - mean) / std)**2))
  
plt.plot(bins, y, '--', color='black')
  
plt.xlabel('Sepal Length')
plt.ylabel('Probability Distribution')
  
plt.title('matplotlib.pyplot.hist() Function Example\n\n',
          fontweight="bold")
  
plt.show()

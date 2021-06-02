import numba 

import numpy as np
from scipy.stats import norm

@numba.njit
def normal_distribution(mu,sigma):
   


    return np.random.normal(mu, sigma, 1).item()



@numba.njit
def generate_normal_rvs(mu:np.array,sigma:np.array) -> np.array:
    if len(mu) != len(sigma):
        raise ValueError(" lengths of arguments are not equal")
    result = []
    for mu,sigma in zip(mu,sigma):
        result.append(normal_distribution(mu,sigma))
    
    return np.array(result)

@numba.njit
def product_dist(base_vector:np.array,*vectors:np.array) -> np.array:
    
    for vector in vectors:
        base_vector = base_vector * vector
    return base_vector


#print(product_dist(np.random))

a = np.array([10,20,30,50])
b=  np.array([2,3,5,6])

print(product_dist(a,b))


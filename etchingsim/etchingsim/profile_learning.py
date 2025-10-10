import numpy as np
import mrafit
from . import etchingdb
from pymongo import MongoClient
from scipy.optimize import minimize

client = MongoClient("mongodb://localhost:27017/")
db = client["your_database"]
collection = db["your_collection"]

pipeline = [
    {"$project": {"keys": {"$objectToArray": "$$ROOT"}}},
    {"$unwind": "$keys"},
    {"$group": {"_id": None, "allKeys": {"$addToSet": "$keys.k"}}}
]
all_keys = list(collection.aggregate(pipeline))
hatbasis = mrafit.wavelet_bases.HatBasis()
n = 10
X = np.linspace(-1, 1, n)
# n_wavelets = hatbasis.get_num_wavelets(X)
# y_val = np.array([hatbasis.wavelet_func((x - 0.5*(X[0] + X[-1]))) for x in X])

# def generate_func(coeffs, funcval):
#     mrafit.utils.scaled_sampling(, X, translate, scaling = 1)
#     for i in range(0, n_wavelets):
#         approx_func +=  coeffs[i] *  hatbasis.wavelet_func(int(n/2), X)
#     return approx_func
 
def merge_funclet(funclet, params):
    n = int(len(funclet)) + 6
    A = np.zeros((n, 3))
    A[0:len(funclet), 0] = funclet
    A[3: len(funclet) + 3, 1] = funclet
    A[6: len(funclet) + 6, 2] = funclet
    return A @ params

def generate_texture(params, depth):
    gaussian_values = np.array([np.exp(-x**2) for x in X])
    funclet = merge_funclet(gaussian_values, params)
    return np.kron(funclet, np.ones(depth))

def get_interpolated_profile(key, resolution = 10):
    collection = etchingdb.get_db_collection()
    actual_curve_points = etchingdb.get_data(collection, key)["points"]
    X = np.linspace(actual_curve_points[0][0], actual_curve_points[-1][0], resolution)
    Xp = [actual_curve_points[i][0] for i in range(len(actual_curve_points))] 
    Yp = [actual_curve_points[i][1] for i in range(len(actual_curve_points))]
    interpolated_curve_points = np.interp(X, Xp, Yp)
    return X, interpolated_curve_points

# A = np.ones((3,3))
# b = np.zeros((3,1))

# def learn(x, b):
#     def objective(learning_params):
#         collection = etchingdb.get_db_collection()
#         for key in all_keys:
        
#             params = np.sigmoid(A @ x + b)
#     learning_params = np.array(A.reshape(-1).tolist() + b.reshape(-1).tolist())
#     bounds = [[-10, 10] for _ in range(len(learning_params))]
#     results = minimize(objective, list(coeffs), bounds=bounds, method = 'Nelder-Mead', options={'maxiter':1000}, tol=10e-5)

# params = [0, 0, 0, 0, 0]
# bias = [0, 0, 0, 0, 0]
# x = [0, 0, 0, 0, 0]

# z = params @ x + bias

# profile = 
# depth = 2
# np.kron()


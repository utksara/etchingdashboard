from etchingsim import profile_learning, etchingdb, fileformat
import matplotlib.pyplot as plt
import numpy as np
from etchingsim import mra_reconstruct, fft_reconstruct
import mrafit

key = '4d2_1d0_3d1_2_5'
key = etchingdb.decode_key(key)
# X, Y = profile_learning.get_interpolated_profile(key, resolution = 100)
            
collection = etchingdb.get_db_collection()
actual_curve_points = etchingdb.get_data(collection, key)["points"]
Xp = [actual_curve_points[i][1] for i in range(len(actual_curve_points))]
Yp = [actual_curve_points[i][0] for i in range(len(actual_curve_points))]

min_xp = np.min(Xp)
Xp = 1*(Xp - min_xp)

# Yp = [x**2 for x in Xp]
# trim = int(len(actual_curve_points)/32)
# Xp = Xp[trim:-trim]
# Yp = Yp[trim:-trim]

resolution = 0.005*(Xp[-1] - Xp[0])
N = 20*len(actual_curve_points)
print("resolution = ", resolution)
X = np.linspace(Xp[0], Xp[-1], N)  # Common X values for all samples
gausslet = mrafit.wavelet_bases.HaarBasis(resolution = resolution)
coeffs, curveball = mra_reconstruct.get_mra_coefficients(Yp, gausslet, X)
print("len curveball", len(curveball))
Y = mra_reconstruct.reconstruction(coeffs, X, gausslet)

# freqs, coeffs, curveball = fft_reconstruct.fourier_curve_reconstruction(np.array(Xp), np.array(Yp))

def func(t, y):
    i = int((t - Xp[0]) / (Xp[-1] - Xp[0]) * (len(Xp) - 1))
    return y[i]

plt.plot(X, curveball)
# plt.plot(X, gausslet.get_1d_wavefunc_data(0, X))
plt.plot(Xp, Yp)
print("num wavelets : ", gausslet.get_num_wavelets(X))
print("num points : ", len(actual_curve_points))
# fileformat.points_to_svg(actual_curve_points, "actual_curve.svg")
plt.show()

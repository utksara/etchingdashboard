import mrafit
import numpy as np

def points_to_func(points):
    x = []
    y = []
    for i  in range(0, len(points)):
        y.append(points[i][0])
        x.append(points[i][1])
    return x, y

def augment_texture(v1, v2):
    if len(v1) < len(v2):
        v1 = np.append(v1, v1[-1]*np.ones(len(v2) - len(v1)))
    elif len(v2) < len(v1):
        v2 = np.append(v2, v2[-1]*np.ones(len(v1) - len(v2)))
    return v1, v2

def reconstruction(coeffs, X, wavelet_basis):
    n_wavelets = wavelet_basis.get_num_wavelets(X)
    approx_func = np.zeros(len(X))
    for i in range(0, n_wavelets):
        approx_func +=  coeffs[i] *  wavelet_basis.get_wavefunc_data(i - int(n_wavelets/2), X)
    return approx_func

def get_mra_coefficients(y, basis_func, X):
    def func(t, y):
        i = int((len(y) - 1) * (t - X[0]) / (X[-1] - X[0]))
        return y[i]
    coeffs, approx_curve, error = basis_func.get_mra_approx(lambda t : func(t, y), X)
    return coeffs, reconstruction(coeffs, X, basis_func)
    
def intermediate_curve(x1, y1, x2, y2, weight):
    y1, y2 = augment_texture(y1, y2)
    X = np.linspace(min(x1[0], x2[0]), max(x1[-1], x2[-1]), max(len(y1), len(y2))) 

    resolution=1
    gausslet = mrafit.wavelet_bases.Gausslet_Basis(resolution)
    # func = curve_functor(X)
    # coeffs1, approx_curve1, error1 = gausslet.get_mra_approx(lambda t : func(t, y1), X)
    # coeffs2, approx_curve2, error2 = gausslet.get_mra_approx(lambda t : func(t, y2), X)
    coeffs1 = get_mra_coefficients(y1, gausslet, X)
    coeffs2 = get_mra_coefficients(y2, gausslet, X)
    weight = 0.5
    coeffs = weight*coeffs1 + (1 - weight)*coeffs2
    approx_curve = reconstruction(coeffs, X, gausslet)

    # plt.plot(x1, y1, label="c1")
    # plt.plot(x2, y2, label="c2")

    # plt.plot(X, np.vectorize(lambda t : func(t, y1))(X), label="c1")
    # plt.plot(X, np.vectorize(lambda t : func(t, y2))(X), label="c2")

    a = 2
    n = len(approx_curve)
    A = np.zeros((n - a, n))
    for i in range(n - a):
        # print(A[i, i : i+a] , np.ones(a))
        A[i, i : i+a] = np.ones(a)/a

    approx_curve = np.matmul(A, approx_curve)
    return X[int(a/2):n - int(a/2)], approx_curve
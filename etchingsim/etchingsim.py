from vtp_to_svg import create_curve
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import vtk

def etching_data_1(csv_path='data.csv'):
    df = pd.read_csv(csv_path)
    data_rows = df.to_numpy()
    target_rows = np.array(data_rows[0:4])
    plottable = np.average(target_rows, axis=0)        
    depth = plottable[0]
    flux_with_time = plottable[1:]
    time_stamp = [250 *(i+1) for i in range(len(flux_with_time))]
    return depth, flux_with_time, time_stamp

def find_interval_and_weight(intervals, x):
    """
    Find the interval where x lies among uniformly spaced intervals
    and return the interval (lower, upper) along with the weight
    relative to the lower bound.

    Args:
        intervals (list): Sorted list of uniformly spaced numbers.
        x (float): The number to locate.

    Returns:
        tuple: ((lower, upper), weight) where weight = (x - lower) / (upper - lower)
    """
    if len(intervals) < 2:
        raise ValueError("Need at least two points to form intervals.")

    step = intervals[1] - intervals[0]

    # if not all(abs(intervals[i+1] - intervals[i] - step) < 1e-9 for i in range(len(intervals)-1)):
    #     raise ValueError("Intervals are not uniformly spaced.")

    if x < intervals[0] :
        return intervals[0], intervals[0], -1
    if x > intervals[-1]:
        return intervals[-1], intervals[-1], -1
        # raise ValueError(f"{x} is outside the interval range [{intervals[0]}, {intervals[-1]}].")
    

    # Find lower bound index
    idx = int((x - intervals[0]) // step)
    lower = intervals[idx]
    upper = intervals[idx + 1]

    weight = (x - lower) / step

    return lower, upper, weight

def find_weight(intervals, x):
    # if x < intervals[0] :
    #     return -1
    # if x > intervals[-1]:
    #     return intervals[-1], intervals[-1], -1
    
    return (x - intervals[0])/(intervals[-1] - intervals[0])

def get_y_distance(poly_data):
    """
    Calculates the vertical distance between the min and max y-coordinates of all points.

    Args:
        poly_data (vtk.vtkPolyData): The VTK polydata object containing the points.

    Returns:
        float: The distance between the minimum and maximum y-coordinates.
    """
    points = poly_data.GetPoints()
    num_points = points.GetNumberOfPoints()

    if num_points == 0:
        return 0.0

    # Get the bounding box to quickly find min and max y
    bounds = poly_data.GetBounds()
    min_y = bounds[2]
    max_y = bounds[3]
    
    return max_y - min_y

def predictive_depth(etch_ion_flux, etch_neu_flux, dep_ion_flux, dep_neu_flux, n_cycles):
    """
    Predictive depth based on the coefficients.
    """
    coefficients = [0.6107013349023487,0.08764549541244973,0.4704964371594592,-0.0021575778435470455,0.21221505218096873]
    depth_0 = coefficients[0]
    k_etch_ion = coefficients[1]
    k_etch_neu = coefficients[2]
    k_dep_ion = coefficients[3]
    k_dep_neu = coefficients[4]
    
    return depth_0 + (k_etch_ion * etch_ion_flux + k_etch_neu * etch_neu_flux - k_dep_ion * dep_ion_flux - k_dep_neu* dep_neu_flux) * n_cycles

def retrieve_curve(m1, m2, m3, m4, n_cycles, data):
    if f"{m1}_{m2}_{m3}_{m4}_{n_cycles}" in data:
        return data[f"{m1}_{m2}_{m3}_{m4}_{n_cycles}"]
    else:
        print(f"{m1}_{m2}_{m3}_{m4}_{n_cycles} point not found") 
        return {"points" :[(i,0) for i in range(0, 100)]}
    
def generate_etching_profile(etch_ion_flux, etch_neu_flux, dep_ion_flux, dep_neu_flux, n_cycles, data, svg_path):
    w1 = find_weight([2,4], etch_ion_flux)
    w2 = find_weight([0.5, 1.5], etch_neu_flux)
        
    p1 = retrieve_curve(2, 0.5, 3, 2, n_cycles, data)["points"]
    p2 = retrieve_curve(2, 1.5, 3, 2, n_cycles, data)["points"]
    # p3 = retrieve_curve(4, 0.5, 3, 2, n_cycles, data)["points"]
    # p4 = retrieve_curve(4, 1.5, 3, 2, n_cycles, data)["points"]
    # if p3 or p4 in None : w2 = 1    
    print(w1, w2)
    create_curve(p1, p2, p1, p2, w1, w2, svg_path)
    d1 = retrieve_curve(2, 0.5, 3, 2, n_cycles, data)["depth"]
    d2 = retrieve_curve(2, 1.5, 3, 2, n_cycles, data)["depth"]
    return d1 * w1 + 2*(1 - w1) * d2 
    
if __name__ == "__main__":
    depth, flux_with_time, time_stamp = etching_data_1()
    print(np.average(flux_with_time[1000:1015]))
    plt.plot(flux_with_time[1000:1015], marker='o', linestyle='-', color='b')
    plt.show()
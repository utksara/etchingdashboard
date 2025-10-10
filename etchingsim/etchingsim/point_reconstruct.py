import numpy as np
def intermediate_curve(x1, y1, x2, y2, weight):
    X = x1
    if len(y1)> len(y2):
        y2 = np.append(y2, y2[-1]*np.ones(len(y1) - len(y2)))
        X = x1
    elif len(y2) > len(y1):
        y1 = np.append(y1, y1[-1]*np.ones(len(y2) - len(y1)))
        X = x2
    # X = np.linspace(min(x1[0], x2[0]), max(x1[-1], x2[-1]), max(len(y1), len(y2))) 
    weight = 1
    Y = weight*y1 + (1 - weight)*y2
    return X, Y
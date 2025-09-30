import mrafit
import numpy as np
from etchingsim import vtp_to_svg
import matplotlib.pyplot as plt 
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["etching_db"]
collection = db["merged_etching_data"]


def augment_texture(v1, v2):
    if len(v1) < len(v2):
        v1 = np.append(v1, v1[-1]*np.ones(len(v2) - len(v1)))
    elif len(v2) < len(v1):
        v2 = np.append(v2, v2[-1]*np.ones(len(v1) - len(v2)))
    return v1, v2

def points_to_func(points):
    x = []
    y = []
    for i  in range(0, len(points)):
        y.append(points[i][0])
        x.append(points[i][1])
    return x, y

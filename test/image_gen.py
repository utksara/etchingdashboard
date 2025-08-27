import sys
sys.path.append('../etchingsim/')
from etchingsim import generate_etching_profile
import json

average_ion_flux = 3000
n_cycles = 70
neutral_particle_flux = 1000
ion_deposition_flux = 3
neu_deposition_flux = 2
output_svg_file = "test_svg.svg"

data = json.load(open("../data/etching_db_new.json"))

generate_etching_profile(average_ion_flux/1000, float(neutral_particle_flux)/1000, ion_deposition_flux, neu_deposition_flux, n_cycles, data, output_svg_file)
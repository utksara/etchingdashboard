import os
import numpy as np
from django.shortcuts import render
from etchingsim import etching_data_1, predictive_depth, generate_etching_profile
from django.conf import settings
import json

def count_cycle(sequence, filter = 4800):
    count = 0
    for i in range(0, len(sequence) - 1):
        if sequence[i+1] > filter and sequence[i] <= filter:
            count += 1
    return count

def threshold_filter(sequence, filter= 2500):
    new_seq = []
    for val in sequence:
        if val > filter:
            new_seq.append(val)
    return np.array(new_seq)

def dashboard_view(request):
    """
    Renders the dashboard page with data and handles user input.
    """
    configs = json.load(open("dashboard/config.json"))
    data = json.load(open("data/etching_db_new.json"))
    # Define your backend data
    
    # variables
    n_cycles = 20
    average_ion_flux = 0.0
    actual_depth = 100
    neutral_particle_flux = request.POST.get('neutral_particle_flux', 500)
    ion_deposition_flux = 3
    neu_deposition_flux = 2
    no_deposition = request.POST.get('no_deposition')
    
    if (no_deposition):
        ion_deposition_flux = 0
        neu_deposition_flux = 0
    
    start_range = int(request.POST.get('start_range', 1000))
    end_range = int(request.POST.get('end_range', 1200)) #len(ion_flux)))
    
    #results
    predicted_depth = 100
    
    # Path to the image files
    image_path = configs["svg_file"]
    csv_file_path = os.path.join(settings.BASE_DIR, 'data', 'etchingdata.csv')
    input_vtp_file = os.path.join(settings.BASE_DIR, 'data', configs["vtp_file"])
    output_svg_file = os.path.join("dashboard", 'static', configs["svg_file"])
    
    # Calculate results
    actual_depth, ion_flux, time_stamp = etching_data_1(csv_file_path)
    selected_ion_flux = ion_flux[start_range:end_range]
    average_ion_flux = np.mean(threshold_filter(selected_ion_flux))
    n_cycles = count_cycle(selected_ion_flux)
    predicted_depth = n_cycles*predictive_depth(average_ion_flux/1000, float(neutral_particle_flux)/1000, ion_deposition_flux, neu_deposition_flux, n_cycles)
    
    # Generate images
    actual_depth = generate_etching_profile(average_ion_flux/1000, float(neutral_particle_flux)/1000, ion_deposition_flux, neu_deposition_flux, n_cycles, data, output_svg_file)
    
    context = {
        'ion_flux': selected_ion_flux.tolist(), # Convert numpy array to list for rendering
        'start_range': start_range,
        'end_range': end_range,
        'average_ion_flux': average_ion_flux,
        'neutral_particle_flux': neutral_particle_flux,
        'n_cycles': n_cycles,
        'image_path': image_path,
        'actual_depth' : actual_depth,
        'predicted_depth' : predicted_depth,
    }
    
    return render(request, 'dashboard.html', context)
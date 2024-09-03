import numpy as np
import scipy as sp
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import csv
import os

#load Times New Roman font for plotting later
font_path = '/nfs/cfs/home3/ucfa/ucfajsr/MBARS/Rock_Abundance/Times_New_Roman.ttf'
times_new_roman_font = fm.FontProperties(fname=font_path)

#define the range of boulders to be considered when binning
MIN_SIZE = 0.05  #lower limit (5 cm in meters)(typically a practical limit: Lorenz et al., 2023)
MAX_SIZE = None  #Upper limit will be set dynamically based on the largest rock diameter in the dataset

#Function Definitions


#developed for this study
def fit_power_law(xdat, ydat, dataset_label, color='blue'):
    '''Function to fit data to a power-law model and plot the best fit curve.'''
    
    #perform linear regression on the log-log data
    log_xdat = np.log10(xdat)
    log_ydat = np.log10(ydat)
    
    #debugging prints
#     print(f"log_xdat: {log_xdat}")
#     print(f"log_ydat: {log_ydat}")
    
    if len(log_xdat) == 0 or len(log_ydat) == 0:
        print("No valid data for power-law fitting.")
        return 0, 0, 0

    slope, intercept, r_value, p_value, std_err = stats.linregress(log_xdat, log_ydat)
    
    #calculate C and b (depending on the formula definition this is also 
    # commonly K and r)
    C = 10**intercept
    b = -slope
    
    #debugging prints
    #print(f"Fitted constants: C={C}, b={b}, R^2={r_value**2}")
    
    #plotting the best fit curve
    fit_line = C * xdat**(-b)
    plt.plot(xdat, fit_line, linewidth=0.5, color=color)
    
    return C, b, r_value**2

#DOESN'T PRODUCE RELIABLE RESULTS
#May be useful to be modified for later studies
def calculate_cumulative_area(C, b, D_min, D_max, AREA):
    """
    Calculate the cumulative fractional area covered by boulders using integration of the power-law model.

    Parameters:
    C (float): The constant from the power-law fit.
    b (float): The exponent (slope) from the power-law fit.
    D_min (float): The minimum diameter of the boulders.
    D_max (float): The maximum diameter of the boulders.
    AREA (float): The total image area.

    Returns:
    float: Cumulative fractional area covered by boulders (as a percentage).
    """
    if b != 3:
        cumulative_area = (np.pi * C / (4 * (3 - b))) * (D_max**(3-b) - D_min**(3-b))
    else:
        cumulative_area = (np.pi * C / 4) * np.log(D_max / D_min)
    
    # Normalize by the total image area and convert to percentage
    fractional_area_percentage = (cumulative_area / AREA) * 100
    return fractional_area_percentage

def calculate_measured_fractional_area(widths, AREA):
    """
    Calculate the fractional area covered by the measured boulders in the dataset.

    Parameters:
    widths (array): Array of boulder diameters.
    AREA (float): The total image area.

    Returns:
    float: Fractional area covered by measured boulders (as a percentage).
    """
    measured_area = np.sum(np.pi * (widths / 2)**2)
    fractional_area_percentage = (measured_area / AREA) * 100
    return fractional_area_percentage

#Heavily modified for this study
def run(path, fnm, dataset_label, diameter_col, cfa_col, area_col, resolution, ManArea=False):
    fullpath = f'{path}{fnm}'
    print(f'Attempting to read data from: {fullpath}\n')
    DeadReturn = ('', [], [], None, None, None, None, None, None, None)
    
    #Attempt to load dataset
    try:
        data = np.loadtxt(fullpath, delimiter=',', skiprows=1, usecols=(diameter_col, cfa_col, area_col), ndmin=2)
        print(f"\nData shape: {data.shape}\n")
    except FileNotFoundError:
        print(f"{fullpath} not found")
        return DeadReturn

    if len(data) == 0:
        print(f"No Boulders in {fullpath}")
        return DeadReturn
    
    #image area for normalizing
    AREA = data[0][2]
    if ManArea:
        AREA = ManArea

    widths = data[:, diameter_col]
    
    #apply lower and upper limits
    widths = widths[(widths >= MIN_SIZE)]
    global MAX_SIZE
    MAX_SIZE = np.max(widths)
    
    #debugging prints
    print(f"Filtered widths: {widths}")
    print(f"Maximum diameter in dataset (Dmax): {MAX_SIZE}")
    
    #sort by diameters to ensure cumulative counts
    sorted_indices = np.argsort(widths)[::-1]
    widths = widths[sorted_indices]
    
    #normalized cumulative number of boulders
    CFAs = np.cumsum(np.ones_like(widths)) / AREA  # Normalize by image area
    
    #unnormalized cumulative number of boulders (for calculating unnormalized C)
    CFAs_unnormalized = np.cumsum(np.ones_like(widths))  # Without normalization by area
    
    # Debugging prints
#     print(f"Cumulative Number of Boulders (Normalized): {CFAs}")
#     print(f"Cumulative Number of Boulders (Unnormalized): {CFAs_unnormalized}")
    
    #fit to the power-law model with normalized CFAs (for plotting)
    C_normalized, b, R2 = fit_power_law(widths, CFAs, dataset_label)
    
    #fit to the power-law model with unnormalized CFAs (for calculating unnormalized C)
    C_unnormalized, _, _ = fit_power_law(widths, CFAs_unnormalized, dataset_label)
    
    #Calculate predicted CNB for diameter range 0.05 m <= D <= Dmax using the unnormalized C
    D_min = 0.05  # Minimum diameter (5 cm in meters)
    D_max = MAX_SIZE  # Maximum diameter in dataset (Dmax)
    
    #predict CNB in the range
    if b != 1:
        predicted_CNB_range = C_unnormalized * ((D_min**(1-b) - D_max**(1-b)) / (b-1))
    else:
        predicted_CNB_range = C_unnormalized * np.log(D_max / D_min)
    
    #calculate cumulative fractional area covered by boulders in the same diameter range
    fractional_area_percentage = calculate_cumulative_area(C_unnormalized, b, D_min, D_max, AREA)
    
    #calculate fractional area covered by measured boulders
    measured_fractional_area_percentage = calculate_measured_fractional_area(widths, AREA)
    
    print(f"Unnormalized C: {C_unnormalized}")
    print(f"Predicted CNB for diameter range [0.05 m, {MAX_SIZE} m]: {predicted_CNB_range}")
    print(f"Cumulative Fractional Area (%): {fractional_area_percentage}")
    print(f"Measured Fractional Area (%): {measured_fractional_area_percentage}")
    
    return fnm, widths, CFAs, C_normalized, b, R2, C_unnormalized, predicted_CNB_range, fractional_area_percentage, measured_fractional_area_percentage

def compare_best_fits(path, dataset_fnms, labels, diameter_col, cfa_col, area_col, resolution, ManArea, save_path):
    '''Compare best fit curves between multiple datasets using a power-law model.'''
    
    plt.figure(figsize=(6, 6))
    
    #define site colors - modify for no. of datasets
    site_colors = {'A': 'green', 'B': 'blue', 'C': 'red'}
    
    #initialize a list to store results for saving statistics
    all_results = []
    
    for fnm, label in zip(dataset_fnms, labels):
        #load and process the dataset
        dataset_result = run(path, fnm, label, diameter_col, cfa_col, area_col, resolution, ManArea)
        dataset_bins, dataset_CFA, dataset_C, dataset_b, dataset_R2, C_unnormalized, predicted_CNB_range, fractional_area_percentage, measured_fractional_area_percentage = dataset_result[1], dataset_result[2], dataset_result[3], dataset_result[4], dataset_result[5], dataset_result[6], dataset_result[7], dataset_result[8], dataset_result[9]
        all_results.append(dataset_result)
        
        #extract the site letter for coloring
        site_letter = label.split('_')[1]  # Assuming label format is 'Site_X_Variation'
        
        #plot the data points with the corresponding color
        plt.scatter(dataset_bins, dataset_CFA, facecolors='none', edgecolors=site_colors[site_letter], linewidths=0.5, label=f'{label} Data')

        #plot the best fit curve for the dataset with the corresponding color
        fit_power_law(dataset_bins, dataset_CFA, label, color=site_colors[site_letter])
        
        #add the best fit RA legend (avoids dupilicates in the legend) 
        plt.plot([], [], color=site_colors[site_letter], label=f'{label}')
    
    plt.xscale('log')
    plt.yscale('log')
    
    plt.xticks([0.05, 0.1, 0.5, 1, 2, 3, 4, 5], ['0.05', '0.1', '0.5', '1', '2', '3', '4', '5'], fontproperties=times_new_roman_font)
    plt.yticks([10**-5, 10**-4, 10**-3, 10**-2], ['10^-5', '10^-4', '10^-3', '10^-2'], fontproperties=times_new_roman_font)

    
    plt.xlabel('Boulder Diameter (m)', fontproperties=times_new_roman_font)
    plt.ylabel('Cumulative Number of Boulders (m$^2$)', fontproperties=times_new_roman_font)
    plt.legend(loc='upper right', prop=times_new_roman_font)
    plt.grid(True, which='both', linestyle='--', linewidth=0.3)
    plt.title(f'Inter-Site Comparison of Power-Law Fits', fontproperties=times_new_roman_font, fontsize=14, weight='bold')
    plt.xlim(0.3, 5)
    #plt.ylim(1, 200) 
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to {save_path}")
    
    plt.show()
    
    # Save statistics
    comparison_stats_filename = os.path.join(os.path.dirname(save_path), f'{"_vs_".join(labels)}_Power_Law_Statistics.csv')
    with open(comparison_stats_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Site', 'C (normalized)', 'b (slope)', 'R^2 Value', 'C (unnormalized)', 'Predicted CNB [0.05 m, Dmax]', 'Cumulative Fractional Area (%)', 'Measured Fractional Area (%)'])
        for label, result in zip(labels, all_results):
            writer.writerow([label, result[3], result[4], result[5], result[6], result[7], result[8], result[9]])
    
    print(f"Comparison statistics saved to {comparison_stats_filename}")

import numpy as np
import scipy as sp
from scipy import optimize as spopt
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import csv
import os

#load Times New Roman font for plotting later
font_path = '/nfs/cfs/home3/ucfa/ucfajsr/MBARS/Rock_Abundance/Times_New_Roman.ttf'
times_new_roman_font = fm.FontProperties(fname=font_path)

#define the range of boulders to be considered when binning
MIN_SIZE = 0.45  # (metres)
MAX_SIZE = 5.45
num_bins = 100

# Function Definitions
def GolomPSDCFA(D, k):
    ''' The Model curves used in Golombek's 2012 work, similar to those used in Li 2018.
        k is fractional area covered by rocks.
        This produces a CFA curve.
    '''
    q = 1.79 + .152 / k
    F = k * np.exp(-q * D)
    return F

def fittoRA(xdat, ydat, dataset_label, color='blue', RNG=[0.4, 4.5]):
    '''Function to fit CFA results to a rock abundance and plot the best fit curve.'''
    fit_xdat = []
    fit_ydat = []
    for i in range(len(xdat)):
        if RNG[0] <= xdat[i] <= RNG[1]:
            fit_xdat.append(xdat[i])
            fit_ydat.append(ydat[i])

    try:        
        popt, _ = spopt.curve_fit(GolomPSDCFA, fit_xdat, fit_ydat, p0=[0.02])
    except Exception as e:
        print(f"Fit failed: {e}")
        return [False], 0, 0, 0

    # Calculate the R2 on the fit
    ybar = np.average(fit_ydat)
    SStot = np.sum((fit_ydat - ybar) ** 2)
    predicted = GolomPSDCFA(fit_xdat, popt)
    SSres = np.sum((fit_ydat - predicted) ** 2)
    R2 = 1 - SSres / SStot

    # Plotting the best fit curve without adding a label to the legend
    xrng = np.linspace(RNG[0], RNG[1])
    plt.plot(xrng, GolomPSDCFA(xrng, popt[0]), linewidth=0.5, color=color)

    return popt, R2


def compare_best_fits(path, dataset_fnms, labels, diameter_col, cfa_col, area_col, resolution, ManArea, save_path):
    '''Compare best fit curves between multiple datasets.'''
    
    plt.figure(figsize=(6, 6))
    
    #define site colors - modify for no. of datasets
    site_colors = {'A': 'green', 'B': 'blue', 'C': 'red'}
    
    #initialize a list to store results for saving statistics
    all_results = []
    
    for fnm, label in zip(dataset_fnms, labels):
        #load and process the dataset
        dataset_result = run(path, fnm, label, diameter_col, cfa_col, area_col, resolution, ManArea)
        dataset_bins, dataset_CFA, dataset_RA, dataset_R2 = dataset_result[1], dataset_result[2], dataset_result[3], dataset_result[4]
        all_results.append(dataset_result)
        
        #extract the site letter for coloring
        site_letter = label.split('_')[1]  # Assuming label format is 'Site_X_Variation'
        
        #plot the data points with the corresponding color
        plt.scatter(dataset_bins, dataset_CFA, facecolors='none', edgecolors=site_colors[site_letter], linewidths=0.5, label=f'{label} Data Points')

        #plot the best fit curve for the dataset with the corresponding color
        fittoRA(dataset_bins, dataset_CFA, label, color=site_colors[site_letter])
        
        #add the best fit RA legend (avoids dupilicates in the legend) 
        plt.plot([], [], color=site_colors[site_letter], label=f'{label} Best Fit RA: {dataset_RA:.2%}')
    
    #plot theoretical curves for different rock abundances and add a single legend entry
    theoretical_RAs = [0.03, 0.05, 0.07, 0.10, 0.20, 1]  # 3%, 5%, 7%, 10%, 20%
    xrng = np.linspace(MIN_SIZE, MAX_SIZE)
    for RA in theoretical_RAs:
        plt.plot(xrng, GolomPSDCFA(xrng, RA), color='gray', linestyle='--', linewidth=0.5, alpha=0.6)

    #add a single legend entry for theoretical curves
    plt.plot([], [], color='gray', linestyle='--', linewidth=0.5, alpha=0.6, label='Theoretical curves for 3%, 5%, 7%, 10%, 20%, 100% RA')
    
    plt.yscale('log')
    plt.xscale('log')
    
    plt.xticks([1, 2, 3, 4, 5], ['1', '2',  '3', '4', '5'], fontproperties=times_new_roman_font)
    plt.yticks(fontproperties=times_new_roman_font)
    
    plt.xlabel('Boulder Diameter (m)', fontproperties=times_new_roman_font)
    plt.ylabel('Cumulative Fractional Area', fontproperties=times_new_roman_font)
    plt.legend(loc='upper right', prop=times_new_roman_font)
    plt.grid(True, which='both', linestyle='--', linewidth=0.3)
    #Change for dataset been run through
    plt.title(f'Inter-Site Comparison of Rock Abundance - MBARS Composite Dataset', fontproperties=times_new_roman_font,  fontsize=14, weight='bold')
    plt.xlim(0.4, 5)
    plt.ylim(1e-5, 1)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to {save_path}")
    
    plt.show()
    
    #save comparison statistics
    comparison_stats_filename = os.path.join(os.path.dirname(save_path), f'{"_vs_".join(labels)}_RA_Statistics.csv')
    with open(comparison_stats_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Site', 'Best Fit RA', 'R^2 Value'])
        for label, result in zip(labels, all_results):
            writer.writerow([label, result[3], result[4]])
    
    print(f"Comparison statistics saved to {comparison_stats_filename}")

    
#Modified
#This expects files with the column format: Diameter - Flag - Image Area
#can be used for both MBARS and manual results
def run(path, fnm, dataset_label, diameter_col, cfa_col, area_col, resolution, ManArea=False):
    fullpath = f'{path}{fnm}'
    print(f'Attempting to read data from: {fullpath}\n')
    DeadReturn = ('', [], [], None, None)
    
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
    
    AREA = data[0][2]
    if ManArea:
        AREA = ManArea

    widths = data[:, diameter_col]
    areas = np.pi * (widths / 2) ** 2
    area_sigs = (np.pi * resolution * 0.5 * widths) ** 2
    
    bins = np.linspace(MIN_SIZE, MAX_SIZE, num_bins)
    CFAs = []
    for i in bins:
        areas_above = areas[widths > i]
        if len(areas_above) == 0:
            CFAs.append(0)
            continue
        t_area = np.sum(areas_above)
        f_area = float(t_area) / AREA
        CFAs.append(f_area)
    
    # Fit to the Golombeck model and return
    opt, R2 = fittoRA(bins, CFAs, dataset_label)
    
    return fnm, bins, CFAs, opt[0], R2

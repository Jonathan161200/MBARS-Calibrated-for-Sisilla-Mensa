#!/usr/bin/env python
# coding: utf-8

# ### Compare to Golombeck and Rapp (1997) Exponential Function

# In[1]:


import Compare_to_GR_Exp  # Import the new comparison module
import os

#list of site letters
#if customised, modify corresponding Compare_to_GR_Exp.py
site_letters = ['A', 'B', 'C']

# Specific dataset variation to compare (Composite)
dataset_variation_to_compare = 'Composite'
#dataset_variation_to_compare = 'Man'
#dataset_variation_to_compare = 'TP'

#Specify path to where MBARS is stored by user
#Here dataset are stored in a sub-folder 'Rock_Abundance'
PATH = '/path<MBARS folder/MBARS/Rock_Abundance/'  #update with your dataset path

#Set columns for Boulder Diameter, CFA, and Area
diameter_col = 0  # boulder diameters 
cfa_col = 1  # flag column
area_col = 2  # area

#resolution for uncertainty calculations
resolution = 0.2867573174999999974  #adjust in accordance to used HiRISE image

#ManArea (optional): Provide this if you want to override the calculated area with a specific value
man_area = None  # Set to None if you don't want to override the calculated area

#Define the subfolder path for saving comparison results
subfolder = os.path.join(PATH, f'Composite_Comparison')

#create the subfolder if it doesn't exist
os.makedirs(subfolder, exist_ok=True)

#prepare to collect dataset filenames and labels
dataset_filenames = []
labels = []

# Loop through each site letter to process the composite datasets
for site_letter in site_letters:
    # Construct the filename and label for the composite dataset
    composite_filename = f'Site {site_letter} for GIS_CFA({dataset_variation_to_compare}).csv'
    composite_label = f'Site_{site_letter}_{dataset_variation_to_compare}'
    
    # Add to lists
    dataset_filenames.append(composite_filename)
    labels.append(composite_label)

# Update save_path to include the new subfolder for the comparison plot
save_path = os.path.join(subfolder, f'{dataset_variation_to_compare}_Sites_Comparison.png')

#call Compare_to_GR_Exp
result = Compare_to_GR_Exp.compare_best_fits(
    path=PATH,
    dataset_fnms=dataset_filenames,  # Pass the list of dataset filenames
    labels=labels,  # Pass the list of labels
    diameter_col=diameter_col,
    cfa_col=cfa_col,
    area_col=area_col,
    resolution=resolution,
    ManArea=man_area,
    save_path=save_path
)

# Process the result
if result:
    print(f"Comparison for {dataset_variation_to_compare} datasets completed successfully.")
else:
    print(f"Comparison for {dataset_variation_to_compare} datasets failed.")


# ### Compare to Power Law Function

# In[1]:


import Compare_to_PowerLaw  # Import the new comparison module
import os

#list of site letters
#if customised, modify corresponding Compare_to_PowerLaw.py
site_letters = ['A', 'B', 'C']

# Specific dataset variation to compare (Composite)
dataset_variation_to_compare = 'Composite'
# Specific dataset variation to compare (Composite)
#dataset_variation_to_compare = 'Man'
# Specific dataset variation to compare (Composite)
#dataset_variation_to_compare = 'TP'

#Specify path to where MBARS is stored by user
#Here dataset are stored in a sub-folder 'Rock_Abundance'
PATH = '/path<MBARS folder/MBARS/Rock_Abundance/'  #update with your dataset path

#Set columns for Boulder Diameter, CFA, and Area
diameter_col = 0  # boulder diameters 
cfa_col = 1  # flag column
area_col = 2  # area

#resolution for uncertainty calculations
resolution = 0.2867573174999999974  #adjust in accordance to used HiRISE image

#ManArea (optional): Provide this if you want to override the calculated area with a specific value
man_area = None  # Set to None if you don't want to override the calculated area

#Define the subfolder path for saving comparison results
subfolder = os.path.join(PATH, f'{dataset_variation_to_compare}_Power_Law_Comparison')

#create the subfolder if it doesn't exist
os.makedirs(subfolder, exist_ok=True)

#prepare to collect dataset filenames and labels
dataset_filenames = []
labels = []

#loop through each site letter to process the composite datasets
for site_letter in site_letters:
    # Construct the filename and label for the composite dataset
    composite_filename = f'Site {site_letter} for GIS_CFA({dataset_variation_to_compare}).csv'
    composite_label = f'Site_{site_letter}_{dataset_variation_to_compare}'
    
    # Add to lists
    dataset_filenames.append(composite_filename)
    labels.append(composite_label)

#Update save_path to include the new subfolder for the comparison plot
save_path = os.path.join(subfolder, f'{dataset_variation_to_compare}_Sites_Comparison.png')

#Call Compare_to_PowerLaw
Compare_to_PowerLaw.compare_best_fits(
    path=PATH,
    dataset_fnms=dataset_filenames,
    diameter_col=diameter_col,
    cfa_col=cfa_col,
    area_col=area_col,
    resolution=resolution,
    ManArea=man_area,
    save_path=save_path
)

print(f"Comparison for {dataset_variation_to_compare} datasets completed successfully")


# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# ### A few checks to make before MBARS is run

# In[1]:


#Check images are accessable
from PIL import Image
import os

image = '/path<MBARSfolder/MBARS/Images/ESP_036925_1985_REDA/ESP_036925_1985_REDA0.PNG' #customise

#check if the file exists
if os.path.exists(image):
    print(f"File {image} exists.")
else:
    print(f"File {image} does not exist.")

#try opening the image
try:
    with Image.open(image) as img:
        img.show()
    print("Image opened successfully.")
except Exception as e:
    print(f"Error opening image: {e}")
    
Image_Area = len(image)*(len(image[0]))
print(f'Image Area:{Image_Area} pixels^2')


# In[2]:


#code to read the worldfile information and check its in the correct format
#define a file path
file_path = '/path<MBARSfolder/MBARS/Images/ESP_036925_1985_REDA/ESP_036925_1985_REDA0.PGw' #customise

#open and read the contents of the world file
with open(file_path, 'r') as file:
    lines = file.readlines()

#Extract the values
pixel_size_x = float(lines[0].strip())
rotation_row = float(lines[1].strip())
rotation_column = float(lines[2].strip())
pixel_size_y = float(lines[3].strip())
upper_left_x = float(lines[4].strip())
upper_left_y = float(lines[5].strip())

#print the extracted values
print(f"Pixel size in x-direction: {pixel_size_x}")
print(f"Rotation term for row: {rotation_row}")
print(f"Rotation term for column: {rotation_column}")
print(f"Pixel size in y-direction: {pixel_size_y}")
print(f"X-coordinate of the center of the upper left pixel: {upper_left_x}")
print(f"Y-coordinate of the center of the upper left pixel: {upper_left_y}")


# In[3]:


# Define the directory path
directory_path = '/nfs/cfs/home3/ucfa/ucfajsr/MBARS/RefData2/'

# Check if the directory exists
if os.path.exists(directory_path):
    print(f"Contents of directory: {directory_path}:")
    # List all files and directories in the specified path
    for item in os.listdir(directory_path):
        print(item)
else:
    print(f"The directory {directory_path} does not exist.")


# In[4]:


#Debugging to check the reference data is 

# import os

# #Assuming MBARS.REFPATH is defined in your script
# MBARS.REFPATH = '/path<MBARS folder/MBARS/RefData/' #customise

# tab_file_path = os.path.join(MBARS.REFPATH, 'RDRCUMINDEX.TAB')

# # Check if the file exists
# if os.path.exists(tab_file_path):
#     print(f"File {tab_file_path} exists.")
# else:
#     print(f"File {tab_file_path} does not exist.")

# # Try reading the file
# try:
#     with open(tab_file_path, 'r') as file:
#         for i in range(2):
#             print(file.readline())
#     print("TAB file read successfully.")
# except Exception as e:
#     print(f"Error reading TAB file: {e}")


# ### Code to Access and Run MBARS

# In[5]:


import MBARS
import matplotlib.pyplot as plt
import scipy.misc as spm
import numpy as np
import time
import threading
'''
set number of images, this is expecting a series of images with the same root name
and numerals at the end, i.e. "root0.PNG" and "root23.PNG"


Possibly consider a way to make this check them all for running instructions first, then run them all in order
This would put more of the user-interface up front.

'''

#Set the global path and filenames to process
PATH = MBARS.BASEPATH

#Function to check and print the contents of the directory
#def check_directory_contents(path):
 #    if os.path.exists(path):
  #       print(f"Directory path exists; contents of the directory {path}:")
   #      for root, dirs, files in os.walk(path):
    #         for name in files:
     #            print(os.path.join(root, name))
     #else:
      #   print(f"The directory {path} does not exist.")

#check_directory_contents(MBARS.BASEPATH)

print(f'MBARS.BASEPATH:{MBARS.BASEPATH}')
print(f'PATH:{PATH}')

#print('MBARS.PATH:{MBARS.PATH}')

#Filenames
filenames = []

#FRAC values to use 
#For InSight image, FRAC values 10,20 did not detect any boulders.
# FRACS = [] #Used for initial run, idenitfied the majority of notable boulders
# in the image but mistook a number of craters for boulders, MBARS struggled most notably
# to classify boulder/non boulder features within the shadow cast by the craters.

FRACS = [15]
#FRACS = [0,5,10,15,20,25,30,35,40]

#Set root name of the image(s) to be processed
#This should be the name of the folder that the images are kept in
#This will be appended by N.PNG by MBARS

#filenames+=['ESP_036925_1985_REDA'] #site A
# filenames+=['ESP_036925_1985_REDB'] #site B
#filenames+=['ESP_036925_1985_REDC'] #site C
filenames+=['ESP_036925_1985_REDS'] #full Sisilla Image

#############################SOME CONTROLS###################
#produce intermediate plots, False unless you are debugging something
plot = False
#for continuing broken runs, use Startat to specify which panel to begin on for the first run
#Keep in  mind that threaded runs do not complete the files in order, use with caution
startat = 0
#Process is largely processer-limited, so benefit to large number of threads is minimal
#setting no limit causes memory errors.
thread_limit = 16


#This function is responsible for processing each image partition
def core(num,gam,plot,manbound,bound,odr_keycard):
    '''core function of the run file, does gamfun and boulder detect
    '''
    seg,good,runfile = MBARS.autobound(num,bound)
    #print 'step 1 done'
    if good:
        if any(seg.compressed()):
            bads = MBARS.boulderdetect_threadsafe(num,seg,runfile,odr_keycard)
            #MBARS.overlapcheck_threadsafe_DBSCAN(num,runfile, odr_keycard, overlap=.001)
            MBARS.overlapcheck_shadbased(num,runfile,odr_keycard)
    if num%200 == 0:
        print ('Done with image %s'%(num))
    return runfile

def thread_run(filename,plot,startat, frac):
    print(f"processing file: {filename}")
    MBARS.FNM, MBARS.ID, MBARS.NOMAP,panels = MBARS.RunParams(filename)
    print(f"\n RunParams output - FNM: {MBARS.FNM},\n ID: {MBARS.ID},\n NOMAP: {MBARS.NOMAP},\n panels: {panels}\n")
    
    MBARS.PATH = '%s%s//'%(PATH,MBARS.FNM)
    print(f"MBARS.PATH: {MBARS.PATH}")
    print(f"\nCalling getangles with ID: '{MBARS.ID}'")
    MBARS.INANGLE, MBARS.SUNANGLE, MBARS.RESOLUTION, MBARS.NAZ, MBARS.SAZ, MBARS.ROTANG = MBARS.start()
    print(f"\nInitialisation values:\n INANGLE: {MBARS.INANGLE},\n SUNANGLE: {MBARS.SUNANGLE},\n RESOLUTION: {MBARS.RESOLUTION},\n "
          f"NAZ: {MBARS.NAZ},\n SAZ: {MBARS.SAZ},\n ROTANG: {MBARS.ROTANG}")
    #set the proportion of the shadow to use here
    bound = MBARS.getimagebound(panels,frac)
    mangam = 0
    manbound = 0
    t1 = time.time()
    
    threads = []
    krange = range(startat,panels)
    print ('%s images to run'%(panels))
    odr_keycard = threading.Lock()
    threads = [threading.Thread(target = core, args=(a,mangam,plot,manbound,bound,odr_keycard),name='%s'%(a)) for a in krange]
    count=0
    for i in range(len(threads)):
        runfile = threads[i].start()
        while threading.active_count() > thread_limit:
            #print( 'Waiting at %s on thread room'%(i))
            #print(threading.enumerate())
            time.sleep(5)
        # make sure the dragging end doesnt get too far behind
        # This way, when it encounters a big image it wont move on too far
        if i>thread_limit:
            threads[i-thread_limit].join()
            if (i-thread_limit)%200 == 0:
                print ('completed thread %s'%(threads[i-thread_limit].name))
        
    #make sure it does not execute any more code until all threads done
    for i in threads:
        i.join()
    
    t2 = time.time()
    #This time is coming up very wrong.....
    ttime = (t2-t1)/3600.
    print ('total time: '+str(ttime)+'hours')
    #this is to note the last running conditions:
    string = "This image was last run with the parameters mangam = %s, manbound=%s. \nIt took %s hours"%(mangam,manbound,ttime)
    record = open('%s%s_runinfo.txt'%(MBARS.PATH,MBARS.FNM),'w')
    for item in string:
        record.write(item)
    record.close()
    return panels

#setup all the parameters before running
#for i in filenames:
    #mangam, manbound = MBARS.FindIdealParams(i)

#Set up the files before running all of them
for i in filenames:
    print (i)
    a,b,c,d = MBARS.RunParams(i)
#actually run the analysis on all of them
for i in filenames:
    for j in FRACS:
        PNLS = thread_run(i,plot,startat,j)
        MBARS.OutToGIS('autobound//','autobound_'+str(j)+'//',PNLS)


# ## Analysis

# In[6]:


import MBARS
import matplotlib.pyplot as plt
import scipy.misc as spm
import numpy as np
import time
#import cPickle as pickle
import threading

from MBARS import gauss, gauss_unnorm,current, getshads, bulkCFA, CFA, fittoRA, shadow
from MBARS import plotCFArefs, PSD, GolomPSDCFA, checkbads, ExamineImage, FindBigs, FindExcluded


# In[7]:


current()


# ### Test getshad

# In[8]:


#runfile = 'autobound/' is set within the autobound function in MBARS.py
#Do not set a runfile. here only num needs to be set
#Below is a test run to check that getshads is constructing the right path
#to the shads files and retrieving them for use in CFA and bulkCFA functions

#Analysis should be undertaken after MBARS_RUN as this way the Path and file
#name are set and can be called. Use #current() to confirm this

#set par
num = 0 #image partition number
runfile = 'autobound/'

#examplepath
#shadow_file_path = '%s%s%s%s_shadows.shad'%(PATH,runfile,FNM,num)
#print(shadow_file_path) 

#Test getshads function
def test_getshads(runfile, num):
    try:
        file_obj = getshads(runfile, num, silenced=False)
        if file_obj:
            print(f"File {file_obj.name} opened successfully.")
            
            import pickle
            
            while True:
                try:
                    data = pickle.load(file_obj)
                    
                    # Print out type and attributes
                    print(f"Loaded data type: {type(data)}")
                    if isinstance(data, shadow):
                        print(f"Data attributes: bouldwid_m={data.bouldwid_m}, measured={data.measured}")
                    else:
                        print(f"Unexpected data type: {type(data)}")
                    
                except EOFError:
                    break
                except Exception as e:
                    print(f"Error during pickle load: {e}")
                    break
        
        file_obj.close()  # Close the file after testing
    except Exception as e:
        print(f"Failed to open or process file: {e}")

# Example usage
test_getshads(runfile, num)


# ### CFA

# In[9]:


#Call CFA
#Use for CFA analysis of individual partitions
#Outputs CFA and SFD csv. files 

#Commented out as this is handled in bulkCFA
# num = 0 #image partition number
# maxd = 10 #max diameter to be considered a boudler

# CFA(runfile,num,maxd)


# ### BulkCFA

# In[10]:


#Call bulkCFA
#Runs CFA protocol on a set of files, averages results, and produces plots and data files
#Outputs filtering parameters, plot of the CFA and RA as a PNG file, CFA data (csv)
#bulkCFA arguements are runfile, maxnum,maxd,fitmaxd,root

#Option 1 will plot your data against the theoretical
#model outlined in Golombeck et al., 2008

#parameters
maxnum = 4 #The number of partitions beings processed
maxd = 10 #The maximum diameter in meters, check csv file
fitmaxd = 10 #The maximum diameter for fitting
root = f'ESP_036925_1985_RED with FRAC at: {FRACS}' #This will be the title of the Plot

bulkCFA(runfile,maxnum,maxd,fitmaxd,root)

print('bulkCFA run completed')


# # Validation

# ### Examine Image

# In[11]:


showblanks = True #set true to show black images
filt = True #set true to apply filtering

ExamineImage(runfile,num, showblanks,filt = True)


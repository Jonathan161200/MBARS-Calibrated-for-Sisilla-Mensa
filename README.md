## Access Statement
The code to operate MBARS is freely available in the supplementary materials of Hood et al., (2022 [1]) or through this link: https://github.com/dhood14/MBARS?tab=MIT-1-ov-file , and was modified for use in this study. Beneath is the accompanying copywrite and permission notice. 

Copyright 2022 Donald Ramsey Hood

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## File Descriptions

### 1)	Core scripts to run MBARS:
* MBARS.py: The modified version of MBARS used in the study. Modifications are noted and explained through ‘#’ comments.
* MBARS_RUN_Sisilla_Mensa.py: The modified version of MBARS_RUN used in the study. Modifications are noted and explained through ‘#’ comments. Used to access MBARS.py and apply it to HiRISE images. 
### 2)	Code to fit to theoretical models:
* Compare_to_Exponential.py: Modified version of ‘GIS_CFA.py’ used to fit MBARS results or manually input datasets to the Exponential function defined in Golombeck and Rapp (1997).
* Compare_to_PowerLaw.py: Extensively modified version of ‘GIS_CFA.py’ used to fit MBARS results or manually input datasets to the Power Law functions defined in Golombeck and Rapp (1997).
* Compare_to_Theoretical_Fits.p: Code to call Compare_to_Exponential.py and Compare_to_PowerLaw.py. 


## Usage Notes
**Dependencies:** All modified scripts utilize standard Python libraries.

**Customization:** Unless noted, the core scripts (MBARS.py and MBARS_RUN_Sisilla_Mensa.py) should not require modification beyond setting user-specific directory paths.

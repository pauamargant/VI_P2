# Information Visualization: Second Practical Work

## Authors
- [Pau Amargant](github.com/pamargant)
- [David Gallardo](github.com/dagallgit)
  
## Description
This repository contains the assignment corresponding to the second practical work for the Information Visualization Course at GCED UPC. The assignment has consisted on creating a multi-view visualization which allows the user to answer a set of questions about traffic accidents in New York City.  

With this objective in mind the Python Altair and Streamlit libraries have been used to create an interactive visualization. The visualization uses traffic accident data from public datasets; one of which contain the traffic accidents information and an additional weather dataset.

Included in this repository are both datasets, which have previously been preprocessed using OpenRefine.

AQUI UNA FOTO DE LA VIS.


## How to run the code
In order to ensure the code run properly we recommend using a dedicated*conda* environment. The project has been tested using a *conda* environment which uses Python 3.12 and the following libraries. This setup has been tested both in  AASSEGURARNOSOOOOOOOOOOOOO Windows 11, Windows Subsystem for Linux and MacOS???. 
- altair
- streamlit
- numpy
- pandas
- geopandas
- geodatasets
In order to set up the required environment we recommend creating a new environment using the following instructions. We provide two different ways to create the environment, using the provided *environment.yml* file or manually installing the required libraries.
- Using conda and environment.yml
```bash
conda env create -f environment.yml
```
- Creating the conda environment manually and installing the required libraries. Note that `<env_name>` must be replaced with the desired name for the environment.
```bash
conda create -n <env_name> python=3.12
conda activate <env_name>
pip install -r requirements.txt
```


### Troubleshooting
In case there are issues related to the installation of the libraries, we recommend trying the alternative installation method. If the issue persists, please contact us.

Furthermore, a prebuilt version of the visualization is also provided in `html` format. This version, which is available in the `char.html` file can be opened in any browser and does not require any additional setup.

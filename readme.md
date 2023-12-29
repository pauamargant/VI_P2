# Information Visualization: Second Practical Work

## Authors
- [Pau Amargant](github.com/pamargant)
- [David Gallardo](github.com/dagallgit)
  
## Description
This repository contains the assignment corresponding to the second practical work for the Information Visualization Course at GCED UPC. The assignment has consisted on creating a multi-view visualization which allows the user to answer a set of questions about traffic accidents in New York City.  

With this objective in mind the Python Altair and Streamlit libraries have been used to create an interactive visualization. The visualization uses traffic accident data from public datasets; one of which contain the traffic accidents information and an additional weather dataset.

Included in this repository are both datasets, which have previously been preprocessed using OpenRefine.

AQUI UNA FOTO DE LA VIS.


## Requirements
In order to ensure the code run properly we recommend using a dedicated*conda* environment. The project has been tested using a *conda* environment which uses Python 3.12 and the following libraries. This setup has been tested both in Windows 11 (Python 3.11, 3.12) and Ubuntu (WSL and Python 3.12, 3.11, 3.10) and MacOS (Python 3.10). 
- altair
- streamlit
- numpy
- pandas
- geopandas
- geodatasets
### Setting up the environment
In order to set up the required environment we recommend creating a new environment using the following instructions. You can try to run the code by manually installing the latest version of the aforementioned librries.
Otherwise, We provide two different ways to create the environment, using the provided *environment.yml* file or manually installing the required libraries. 

- Creating the conda environment manually and installing the required libraries (_faster_). Note that `<env_name>` must be replaced with the desired name for the environment.
```bash
conda create -n <env_name> python=3.12
conda activate <env_name>
pip install -r requirements.txt
```
- Using conda and environment.yml (_takes longer_)
```bash
conda env create -f environment.yml
```
## Running the Report and the Visualization

### Report
In order to view the report, we provide a *Jupyter Notebook* which contains the design process and the answers to the questions. The notebook can be opened using Google Colab or Jupyter Notebook. In order to run the notebook, the required libraries must be installed, a cell with the required commands is provided in the notebook.

In order to ran the notebook the following files must be placed in the same location as the notebook:
- `dataset_v1.csv`
- `weather.csv`
- `graphs.py`
- `requirements.txt`
Please note that the visualizations are preloaded in the notebook but if not ran in Google Colab, the visualizations might not be displayed. In order to view the visualizations, please run the code.

### Visualization
In order to run the visualization, the following command must be executed in the terminal. This will open a new tab in the browser with the visualization. Please run inside the suitable conda environment.
```bash
streamlit run DavidG_PauA_streamlit_site.py
```
In case issues arise, you can run the premade html visualization by opening the `visualization.html` file in a browser.

### Troubleshooting
In case there are issues related to the installation of the libraries, we recommend trying the alternative installation method. If the issue persists, a prebuilt version of the visualization is also provided in `html` format. This version, which is available in the `chart.html` file can be opened in any browser and does not require any additional setup.


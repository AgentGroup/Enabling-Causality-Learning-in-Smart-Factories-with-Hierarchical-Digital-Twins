# Enabling Causality with Digital Twins
Shared repository for experiment reproduction.

Needed Python packages are stored in the "requirements.txt" file. Requires Python3.8 for packages compatibility.

To start the simulation, run the following files:
- "run_me.bat" for Windows;
- "run_me.sh" for Linux and MacOS.

The file will start the simulation and, at the end of it, will open the Jupyter Notebook to launch the causal inference 
with data generated from the last simulation run. 

Simulation parameters are stored in "/manufacturing_model/Model Base Settings.txt" file.
At each run, the setting file is saved in the associated Log folder. 

Log folders are divided in:
- "/manufacturing_model/logs", where generated files are stored;
- and "/manufacturing_model/archive/logs" where the generated files are zipped. 

The two aforementioned folders are completely identical in their contents. The distinction has been made in order to 
facilitate the GitHub uploading and sync.

When the simulation is finished, the project Jupyter Notebook is opened. Inside, the code handles the necessary files 
and moves the newest dataset from "/manufacturing_model/logs/" to "causal_model/dataset/" folder. Here, the last 
causal_model run is deleted, a new folder is generated, then data is used in order to train the causal network 
representing the manufacturing model.

Further information about the experiment available here: 
*link to the paper

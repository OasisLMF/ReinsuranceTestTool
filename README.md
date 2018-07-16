<img src="https://oasislmf.org/packages/oasis_theme_package/themes/oasis_theme/assets/src/oasis-lmf-colour.png" alt="Oasis LMF logo" width="250"/>

# ReinsuranceTestTool
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/OasisLMF/ReinsuranceTestTool/master)

Test tool for new Oasis reinsurance functionality.
A library of worked examples will be created that will be used to validate: 
* the interpretation of the Open Expousre Data (OED) input format
* the execution logic of the Oasis FM

## Setting up the environment

### Local install (Linux)

The pre-requisites for the system on an Ubuntu based system are listed in apt.txt. These can be installed by running:

```
cat apt.txt | xargs apt-get install -y
```

If using another distribution then the comparable packages will need to be identified and installed, or alternatively use a Docker image.

We recommend using a Python virtual environment for running the excercises. To set up the your virtual environment, run the following commands in the project root directory:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter nbextension enable --py --sys-prefix qgrid

pip install ipykernel
ipython kernel install --user --name=ReinsuranceTestTool
```

## Running the test tool
The test tool can either be ran directly from the command line using "reinsurance_tester.py", or via the Jupyter note book "run_test.ipynb".

## License
The code in this project is licensed under BSD 3-clause license.

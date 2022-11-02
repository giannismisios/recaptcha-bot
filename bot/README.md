# Recaptcha Bot

## Description 
The current bot is purposed to automatically resolve the recaptcha model assisted by the BiT trained model. It loads the model and then it can run in a loop multiple times in order to be able to evaluate the results.

## Requirements
1. Setup a conda environment with the requirements.txt file.
2. Download chrome selenium driver for your OS from https://chromedriver.chromium.org/downloads.
3. Download the provided recaptcha model from https://drive.google.com/drive/folders/1lKDBJNnOz6V5R7VLwNzdnzYlQJl_T5so?usp=sharing.
4. Configure the config.ini file with the paths for the model and the selenium drivers 


## How to run
1. Run the demo-page 
2. Set on config.ini how many times you need the bot to run.
3. Install conda requirements of conda environment ``conda install -f requirements.txt``
4. After activating your conda environment that you installed earlier run
``python run.py``

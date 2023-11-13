# PDF2QA-API
This repository consists of the modules necessary for the PDF2QA API endpoints.

## Contents
- **requirements.txt** contains the all modules required to run the API.
- **environment.yml** contains the environment file required to set up a conda enviorment.
- **app/api/pdf2qaconverter.py** contains the utility functions used by the API in the form of a class (All converter related functions can go here).
- **app/api/pdf2qa-api.py** contains the API endpoint used to upload the PDF file (All API related functions can go here).
- **app/api/openai_key.env** contains the OpenAI key stored as an environment variable. Create a .env file with the same name and store the key in the directory *app/api*.
    ```
    OPENAI_API_KEY=your_key_goes_here
    ```

## Getting Started
- Clone the repository.
- Install [Python](https://wiki.python.org/moin/BeginnersGuide/Download) by following the official guide.
- Set up a virtual environment
    - Once you have Python installed, it is a good practice to create a virtual python environment. Virtual environments provide a clean working space for your Python packages to be installed so that you do not have conflicts with other libraries you install for other projects.  
    To create a virtual environment, Python supplies a built in venv module which provides the basic functionality needed for the virtual environment setup. Running the command below will create a virtual environment named "pdf2qa-api-env" inside the current folder you have selected in your terminal / command line:
        ```
        python -m venv pdf2qa-api-env
        ```
        Once you've created the virtual environment, you neeed to activate it. On widnows, run:

        ```
        pdf2qa-api-env\Scripts\activate
        ```
        On Unix or MacOS, run: 
        ```
        source pdf2qa-api-env/bin/activate
        ```
        Once, the environment is activated, run the following command to install libraries from the **requirements.txt** file:
        ```
        pip install -r requirements.txt
        ```
    - If using a conda environment, create a conda environment with the following command:
        ```
        conda env create -f environment.yml
        ```
        If the above command throws any error, please create the environment first using the command:
        ```
        conda create -n pdf2qa-api python=3.9.17
        ```
        Activate the conda environment by running the command:
        ```
        conda activate pdf2qa-api
        ```
        Then install the requirements file by running the command:
        ```
        pip install -r requirements.txt
        ```
- Run the API on local server using *uvicorn* with the following command in the *app/api/* directory:
    ```
    uvicorn pdf2qa-api:app --reload
    ```
- To test the API endpoint, you can use tool like [Postman](https://www.postman.com/).
# Deployment
The proof-of-concept system comprises two main artefacts:
- Backend [Flask app](https://flask.palletsprojects.com/en/2.0.x/) responsible for:
  - serving patient data from a CSV file on disk to the UI 
  - performing inference using the predictive models and returning risk stratification information
- WebUI demonstrator built with [Vue.js](https://vuejs.org/) implementing [NHS.UK frontend components](https://nhsuk.github.io/nhsuk-frontend/) 
  (in line with the [NHS Digital Service design system](https://service-manual.nhs.uk/design-system/components))
  
As the system is an early stage pre-alpha demonstrator, these components are configured to be deployed side-by-side on 
the same physical host.
The following instructions detail the steps required to produce a containerised production build or alternatively run a 
local development server.

## Importing Example Data Records
The components operate as a standalone proof-of-concept and hence does not depend on access to external patient record data.
To make example records available for testing and demonstration purposes, a CSV file is required containing rows of patient data and columns
for each of the fields identified by the `Original_Data_Fields` key in [config/data_descriptions.json](../config/data_description.json#L2).

Data is read from the CSV file by the backend Flask app at runtime and served to the WebUI to be displayed.
For this mechanism to function correctly, the example data should be saved to a file named `example_records.csv`,
which in turn should be placed in the `records` directory. Failure to include the required record data in `records/example_records.csv` 
will prevent the data loading code, and in turn the record API endpoints, from operating.

To generate fake data with the necessary columns and fake rows, please see the documentation for the [fake data generator](../fake_data_generation/README.md).

To train the models using real or fake data, please see the documentation for [training](../training/README.md).

## Recommended: Containerised Build 

Deployment of a production build of the API service and WebUI is achieved with Docker containers. 

#### Pre-requisites
* [Docker](https://docs.docker.com/get-docker/)

#### Installation
The following steps should be executed from the top level of the repository.

1) **Generate a flask secret key**
  ```shell
  python3 -c 'import os; print(os.urandom(16))'
  ```
  - Store this value in `SECRET_KEY` in [ltss/\_\_init\_\_.py](../ltss/__init__.py#L16)
2) **Build the containers**
  ```shell
  $ docker build -f deploy/LTSS_API.Dockerfile -t ltss:api .
  $ docker build -f deploy/LTSS_WebUI.Dockerfile -t ltss:webui .
  ```
3) **Create a docker network for the containers to communicate**
  ```shell
  $ docker network create ltss
  ```
4) **Launch both containers**
  ```shell
  $ docker run -d --rm --network=ltss -v $PWD/records:/app/records --name=ltss-api ltss:api
  $ docker run -d --rm --network=ltss -p 8090:8090 --name=ltss-webui ltss:webui
  ```
  - The `ltss-api` container uses a mapped volume to make the patient record file on the host available to the Flask app
  running in the container
5) **Navigate to WebUI homepage in browser** <br />
  >[http://localhost:8090](http://localhost:8090) 

## Development Mode: Local Server
Launching both components as part of a local development environment makes use of the Flask and vue-cli-service development
and debugging servers. This method of deployment make various convenient debugging tools available (e.g. hot-reload of code changes for
both frameworks and the Vue.js devtools extensions) but require the successful installation of pre-requisite software stacks.

### Flask app

#### Pre-requisites
* [Python 3.8](https://docs.python.org/3.8/)
* [pip package installer](https://pip.pypa.io/en/stable/)

#### Installation
The following steps should be executed from the top level of the repository.
1) **Install required python packages**
  ```shell
  $ pip install -r requirements.txt
  ```

2) **Generate a flask secret key**
```shell
  python3 -c 'import os; print(os.urandom(16))'
  ```
  - Store this value in `SECRET_KEY` in [ltss/\_\_init\_\_.py](../ltss/__init__.py#L16)

3) **Launch Flask development server**
  ```shell
  $ FLASK_APP=ltss:create_app FLASK_ENV=development FLASK_DEBUG=1 python3 -m flask run --host=0.0.0.0
  ```
  This command can be broken down as follows:
  * `FLASK_APP=ltss:create_app` - Indicate the method in the `ltss` package that will construct the flask app. 
  * `FLASK_ENV=development FLASK_DEBUG=1` - Instruct Flask to launch in development mode with debugging enabled (enables code hot-reload).
  * `python3 -m flask run --host=0.0.0.0` - Launch Flask on the local host machine.

4) **Verify Flask app responds to api requests and returns record data**
  ```shell
  $  curl -X GET http://localhost:5000/api/records
  ```
### WebUI

#### Pre-requisites
* [nodejs](https://nodejs.org/en/download/package-manager/)
* [npm](https://docs.npmjs.com/cli/v7/configuring-npm/install)

#### Installation
The following steps should be executed from the `webui` directory of the repository.
1) **Install required npm packages**
  ```shell
  $ npm install
  ```
2) **Launch vue development server**
  ```shell
  $ npm run serve -- --port 8090
  ```
3) **Navigate to WebUI homepage in browser** <br />
  >[http://localhost:8090](http://localhost:8090)

   

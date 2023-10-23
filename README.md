# ParcelLab Data transformer Service
This service is used to:
- receive and validate api calls/files from client
- transform data
- send it to parcellab in correct format

**Transformer**

Transformers are used to transform the data received by the client to ParcelLab data model format

To add a new transformer you need to create a class that inherits `BaseTransformer`, add an input data schema and implement 
`_transform()` method that should transform input data into ParcelLab DataModel.

In this POC project, we assumed we have 2 consumer companies **MoezGmbH** and **NadhemGmbH**, each one uses a different data input format.
- MoezGmbH uses the API to send webhook on every new tracking request
- NadhemGmbH uses a file based tracking creation using csv files

# Development
**Requirements**

- Python 3.9
- Pipenv

**Setup**

- Setup a db database the way you prefer (in a poc context we will use sqlite)
- Create the environment file: `touch .env`
- Install dependencies: `pipenv install --dev`

**Launch**

- Enable the virtual environment: `pipenv shell`
- `flask run` to launch the 🚀
- `celery -A app.celery worker` to run celery

**Tests**

You can run the tests using: `pipenv run pytest`


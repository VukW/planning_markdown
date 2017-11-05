# Description  

This repo contains 3 main parts.

1. [Web Service](docs/web-service) is aimed to markdown appartments plannings. It shows a picture, user mark its edges and walls, and service save new markdown to the database (actually `.json` file).
2. [Data cleaning procedures](docs/data-cleaning) take db file and prepare the dataframes for future ML model.
3. [Models](models) load already tuned models, and predict markdown for every image in the db.


Learning models is out of scope here; the relevant code is located at [planning_nn_model](../planning_nn_model) repo.
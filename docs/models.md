# Models using

Uses an already fitted Keras model, and predict markdowns for new images Script-to-run is `models_prediction.py`, while other code is located at `models` folder. 

For each image url in the DB, it tries to predict a correct markdown. Script do: 

1. Uses a corners model to predict if pixel is a corner (for each pixel on the image)
2. Clusters predicted pixels to left one point for each corner
3. Predicts if there is an edge between every pair of corners
4. Saves a DB with a predicted markdown in the format appropriate for web-service. Predictions are saved at `%DBFILENAME%.json-predicted.json`

## How to run

`python models_prediction.py`
# -*- coding: utf-8 -*-
from dotenv import find_dotenv, load_dotenv


# find .env automagically by walking up directories until it's found, then
# load up the .env entries as environment variables
load_dotenv(find_dotenv())

# for demo purpose save a file in the models directory
f = open("models/demo-model.txt", "a")
f.write("This could have been a trained model...")
f.close()

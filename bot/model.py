import numpy as np
import tensorflow as tf
from tensorflow import keras
#importing the os module
import os
import logging
import configparser
logger = logging.getLogger("model")
logger.setLevel(logging.DEBUG)

#to get the current working directory
directory = os.getcwd()


logger.debug("Current logging directory is %s",directory)

config = configparser.ConfigParser()
config.read('config.ini')
logger.debug('Path to model is %s',config['MODEL']['pathtomodel'])
loaded_model = keras.models.load_model(config['MODEL']['pathtomodel'])
CROP_TO=300
def predict_image_label(image):
    preprocessed_image = __preprocess_image_inference(image)
    logits = loaded_model(preprocessed_image)
    if len(logits.shape) > 1:
      logits = tf.reshape(logits, [-1])
    scores = [1.0/(1.0 + np.exp(-lgt))*100 for lgt in logits]
    logger.debug("Predicted scores: %s",scores)
    return scores


def __preprocess_image_inference(image):
  img_reshaped = tf.reshape(image, [1, image.shape[0], image.shape[1], image.shape[2]])
  img_reshaped=tf.image.resize(img_reshaped, [CROP_TO, CROP_TO])
  image = tf.image.convert_image_dtype(img_reshaped, tf.float32)
  return image

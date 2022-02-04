#!/usr/bin/env python
# coding: utf-8
"""
Object Detection From TF2 Checkpoint
====================================
"""

# %%
# Download the test images
# ~~~~~~~~~~~~~~~~~~~~~~~~
# First we will download the images that we will use throughout this tutorial. The code snippet
# shown bellow will download the test images from the `TensorFlow Model Garden <https://github.com/tensorflow/models/tree/master/research/object_detection/test_images>`_
# and save them inside the ``data/images`` folder.
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging (1)]
os.environ["CUDA_VISIBLE_DEVICES"]="0"	    # Use GPU
import pathlib
import tensorflow as tf
from tensorflow.python.client import device_lib
from datetime import datetime
from pascal_voc_writer import Writer
tf.get_logger().setLevel('ERROR')           # Suppress TensorFlow logging (2)

# Enable GPU dynamic memory allocation
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

#We need to get the images captured by the sage node
IMAGE_PATHS = []

#image director
temp_image_dir = "/raid/AoT/sage/000048B02D15BC7D/bottom/2021/08/31/"
#output directory
xml_output_dir = "/raid/AoT/image_label_xmls/08-31-2021/new_xmls/"

for filename in os.listdir(temp_image_dir):
    for picture in os.listdir(temp_image_dir + filename):
        IMAGE_PATHS.append(os.path.join(temp_image_dir + filename, picture))

# %%
# Download the model
# ~~~~~~~~~~~~~~~~~~
# The code snippet shown below is used to download the pre-trained object detection model we shall
# use to perform inference. The particular detection algorithm we will use is the
# `CenterNet HourGlass104 1024x1024`. More models can be found in the `TensorFlow 2 Detection Model Zoo <https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md>`_.
# To use a different model you will need the URL name of the specific model. This can be done as
# follows:
#
# 1. Right click on the `Model name` of the model you would like to use;
# 2. Click on `Copy link address` to copy the download link of the model;
# 3. Paste the link in a text editor of your choice. You should observe a link similar to ``download.tensorflow.org/models/object_detection/tf2/YYYYYYYY/XXXXXXXXX.tar.gz``;
# 4. Copy the ``XXXXXXXXX`` part of the link and use it to replace the value of the ``MODEL_NAME`` variable in the code shown below;
# 5. Copy the ``YYYYYYYY`` part of the link and use it to replace the value of the ``MODEL_DATE`` variable in the code shown below.
#
# For example, the download link for the model used below is: ``download.tensorflow.org/models/object_detection/tf2/20200711/centernet_hg104_1024x1024_coco17_tpu-32.tar.gz``

# Download and extract model
def download_model(model_name, model_date):
    base_url = 'http://download.tensorflow.org/models/object_detection/tf2/'
    model_file = model_name + '.tar.gz'
    model_dir = tf.keras.utils.get_file(fname=model_name,
                                        origin=base_url + model_date + '/' + model_file,
                                        untar=True)
    return str(model_dir)

MODEL_DATE = '20200711'
# model can be swapped out for higher accuracy but not needed because we only need people detections
# As of 10/31/2021, we have noticed a problem with the lighting and directories in the images - problems for the model detection
MODEL_NAME = 'centernet_hg104_1024x1024_coco17_tpu-32'
PATH_TO_MODEL_DIR = download_model(MODEL_NAME, MODEL_DATE)

# %%
# Download the labels
# ~~~~~~~~~~~~~~~~~~~
# The coode snippet shown below is used to download the labels file (.pbtxt) which contains a list
# of strings used to add the correct label to each detection (e.g. person). Since the pre-trained
# model we will use has been trained on the COCO dataset, we will need to download the labels file
# corresponding to this dataset, named ``mscoco_label_map.pbtxt``. A full list of the labels files
# included in the TensorFlow Models Garden can be found `here <https://github.com/tensorflow/models/tree/master/research/object_detection/data>`__.

# Download labels file
def download_labels(filename):
    base_url = 'https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/data/'
    label_dir = tf.keras.utils.get_file(fname=filename,
                                        origin=base_url + filename,
                                        untar=False)
    label_dir = pathlib.Path(label_dir)
    return str(label_dir)

# LABEL_FILENAME holds all the classes, their names, IDs and descriptions: LABEL ID 1 = person
LABEL_FILENAME = 'mscoco_label_map.pbtxt'
PATH_TO_LABELS = download_labels(LABEL_FILENAME)

# %%
# Load the model
# ~~~~~~~~~~~~~~
# Next we load the downloaded model
import time
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
# USED TO TRACK HOW LONG A SCRIPT IS RUNNING FOR IN END EQUATION
START_OF_SCRIPT = time.time()

PATH_TO_CFG = PATH_TO_MODEL_DIR + "/pipeline.config"
PATH_TO_CKPT = PATH_TO_MODEL_DIR + "/checkpoint"

print('Loading model... ', end='')
start_time = time.time()

# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(PATH_TO_CFG)
model_config = configs['model']
detection_model = model_builder.build(model_config=model_config, is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(PATH_TO_CKPT, 'ckpt-0')).expect_partial()

@tf.function
def detect_fn(image):
    """Detect objects in image."""

    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)

    return detections

end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))




# check predict and post processing
# raise to 75 threshold

# %%
# Load label map data (for plotting)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Label maps correspond index numbers to category names, so that when our convolution network
# predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility
# functions, but anything that returns a dictionary mapping integers to appropriate string labels
# would be fine.

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS,
                                                                    use_display_name=True)

# %%
# Putting everything together
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The code shown below loads an image, runs it through the detection model and visualizes the
# detection results, including the keypoints.
#
# Note that this will take a long time (several minutes) the first time you run this code due to
# tf.function's trace-compilation --- on subsequent runs (e.g. on new images), things will be
# faster.
#
# Here are some simple things to try out if you are curious:
#
# * Modify some of the input images and see if detection still works. Some simple things to try out here (just uncomment the relevant portions of code) include flipping the image horizontally, or converting to grayscale (note that we still expect the input image to have 3 channels).
# * Print out `detections['detection_boxes']` and try to match the box locations to the boxes in the image.  Notice that coordinates are given in normalized form (i.e., in the interval [0, 1]).
# * Set ``min_score_thresh`` to other values (between 0 and 1) to allow more detections in or to filter out more detections.
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings

def load_image_into_numpy_array(path):
    """Load an image from file into a numpy array.
    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.
    Args:
      path: the file path to the image
    Returns:
      uint8 numpy array with shape (img_height, img_width, 3)
    """
    return np.array(Image.open(path))

def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    #input_tensor = tf.convert_to_tensor(np.expand_dims(image, 0), dtype=tf.float32)
    input_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    #detections = detect_fn(input_tensor)
    input_tensor = input_tensor[tf.newaxis,...]
    # Run inference
    #output_dict = model(input_tensor)
    output_dict = detect_fn(input_tensor)
    keys = output_dict.keys()
    #keys = output_dict.keys()
    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key:value[0, :num_detections].numpy() 
                   for key,value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                output_dict['detection_masks'], output_dict['detection_boxes'],
                 image.shape[0], image.shape[1])      
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                       tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()
    return output_dict

def write_label_xmls(model, image_path):
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    file_name = os.path.basename(image_path)
    file_name = file_name.replace('+0000', '') #remove unnecessary information in time
    var_date_time = file_name[:len(file_name)-4].split("T")
    var_date_str, var_time_str = var_date_time[0], var_date_time[1]
    var_time_object = datetime.strptime(var_time_str, "%H:%M:%S")
    var_date_object = datetime.strptime(var_date_str, "%Y-%m-%d")
    # specify the hours of the day you wish to run
    if var_date_object.day > 0 and var_date_object.month >= 0 and 13 <= var_time_object.hour <= 22:
        image_np = np.array(Image.open(image_path))
        # Actual detection.
        output_dict = run_inference_for_single_image(model, image_np)
        im_width, im_height = image_np.shape[1], image_np.shape[0]

        for data in output_dict:
            classes = output_dict['detection_classes']
            boxes = output_dict['detection_boxes']
            scores = output_dict['detection_scores']
            writer = Writer(image_path, im_width, im_height)
            for cls, box, score in zip(classes, boxes, scores):
                left, right, top, bottom = box[1] * im_width, box[3] * im_width, box[0] * im_height, box[2] * im_height
                cls = cls + 1
                if cls in category_index and score >= .5: # .55 good enough to keep pictures around with people in background
                    # doesnt keep the data getting from getting cut off and creating time gaps from pedestrian detection code
                    # .6+ gives data and could be an end threshold for when we have perfected the pedestrian detection code
                    name = category_index[cls]['name']
                    writer.addObject(name, int(left), int(top), int(right), int(bottom))

        path_to_xml = xml_output_dir + os.path.basename(str(image_path)).replace("jpg","xml")
        writer.save(path_to_xml)

for image_path in IMAGE_PATHS:
    xml_path = xml_output_dir + os.path.basename(str(image_path)).replace("jpg", "xml")
    if pathlib.Path(xml_path).is_file() is False:
        write_label_xmls(detection_model, image_path)

# sphinx_gallery_thumbnail_number = 2
# tracks the end time of the script
END_OF_SCRIPT = time.time()
# print the overall runtime of the object detection code for however many hours are specified
print("RUNTIME: ", (END_OF_SCRIPT - START_OF_SCRIPT) / 120, " HOURS")
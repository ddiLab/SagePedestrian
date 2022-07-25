# TO RUN THIS SCRIPT IN THE BACKGROUND DO THE FOLLOWING COMMANDS:
# 1) python plot_object_detection.py
# 2) CTRL + Z
# 3) bg
# 4) jobs
# 5) disown %JOB NUMBER HERE
#!/home/users/justind/.conda/envs/tf_gpu/bin/
#!/usr/bin/env python
# coding: utf-8
"""
Object Detection From TF2 Checkpoint
====================================
"""
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

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

#We need to get the images captured by the sage node
IMAGE_PATHS = []

# Check to see if the user wants a specific date ran, otherwise the default is the current date
import sys
output_dir_date = ""
if len(sys.argv) > 2: # wrong number of arguments
    print("\n Format: python plot_object_detection.py date")
    print("Where date = yyyy/mm/dd ")
    quit()
if len(sys.argv) == 2: # have an input date
    current_date = sys.argv[1] + "/"
    output_dir_date = sys.argv[1]
    new_dir = sys.argv[1]
    new_dir = new_dir.split("/")
    output_dir_date = new_dir[1] + "-" + new_dir[2] + "-" + new_dir[0] + "/" # reformatting to output format
now = datetime.now()
month = "%02d" % (now.month)
day = "%02d" % (now.day)
year = "%04d" % (now.year)
if len(sys.argv) == 1: # default to current time
   current_date = year + "/" + month + "/" + day + "/"
   output_dir_date = month + "-" + day + "-" + year + "/"

temp_image_dir = "/raid/AoT/sage/000048B02D15BC7D/bottom/" + current_date
xml_output_dir = "/raid/AoT/image_label_xmls/" + output_dir_date # directory is created if it does not exist later

for filename in os.listdir(temp_image_dir): # raw image directory
    for picture in os.listdir(temp_image_dir + filename):
        # print("Pic: ", picture)
        if os.path.getsize((os.path.join(temp_image_dir + filename, picture))) <= 0:
            print("Corrupted file found, terminating program")
            quit() 
        IMAGE_PATHS.append(os.path.join(temp_image_dir + filename, picture))

# Download and extract model
def download_model(model_name, model_date):
    base_url = 'http://download.tensorflow.org/models/object_detection/tf2/'
    model_file = model_name + '.tar.gz'
    model_dir = tf.keras.utils.get_file(fname=model_name,
                                        origin=base_url + model_date + '/' + model_file,
                                        untar=True)
    return str(model_dir)

MODEL_DATE = '20200711'
#MODEL_NAME = 'efficientdet_d4_coco17_tpu-32'
#Original model below - takes longer and has a bit less accuracy, MODEL_DATE is the same for both models
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

# LOAD THE MODEL
import time
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder

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

# %%
# Load label map data (for plotting)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Label maps correspond index numbers to category names, so that when our convolution network
# predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility
# functions, but anything that returns a dictionary mapping integers to appropriate string labels
# would be fine.

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings

def load_image_into_numpy_array(path):
    return np.array(Image.open(path)) # Load image from file into numpy array

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

file_hour = 13          
last_hour = file_hour
file_date = " "

def write_label_xmls(model, image_path):
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    file_name = os.path.basename(image_path)
    file_name = file_name.replace('+0000', '') #remove unnecessary information in time
    var_date_time = file_name[:len(file_name)-4].split("T")
    var_date_str, var_time_str = var_date_time[0], var_date_time[1]
    var_time_object = datetime.strptime(var_time_str, "%H:%M:%S")
    var_date_object = datetime.strptime(var_date_str, "%Y-%m-%d")
    
    file_date = str(var_date_object.year) + "/" + "{:02d}".format(var_date_object.month) + "/" + "{:02d}".format(var_date_object.day)
    
    xml_output_dir = "/raid/AoT/image_label_xmls/" + "{:02d}".format(var_date_object.month) + "-" + "{:02d}".format(var_date_object.day) + "-" + str(var_date_object.year) + "/"
    
    # specify the hours of the day you wish to run
    if var_date_object.day > 0 and var_date_object.month >= 0 and 13 <= var_time_object.hour <= 22: # change this 13 to run more than 1 hour
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
                if cls in category_index and score >= .5: # .5 Threshold for accuracy on xml objects
                    name = category_index[cls]['name']
                    writer.addObject(name, int(left), int(top), int(right), int(bottom))

        path_to_xml = xml_output_dir + os.path.basename(str(image_path)).replace("jpg","xml") # Get the xml files 
        writer.save(path_to_xml)
        print("Done: ", os.path.basename(path_to_xml))
        print("Hour: ", file_hour)

        return var_time_object.hour, file_date, True    #return true if the file was processed

    return var_time_object.hour, file_date, False   #return false since the file was not processed

if not os.path.isdir(xml_output_dir): # creation of xml output directory if it does not exist
    os.mkdir(xml_output_dir)

from subprocess import Popen
import pedestrian_detection

count = 0

# For running pedestrian_detection.py
for image_path in IMAGE_PATHS:# add the .xml files into the correct directories
    xml_path = xml_output_dir + os.path.basename(str(image_path)).replace("jpg", "xml")
    file_hour, file_date, processed = write_label_xmls(detection_model, image_path)
# Runs pedestrian_detection.py with "plot" to True so it writes to DB
pedestrian_detection.main(interval=-1, date=file_date, plot=True, initial=True)

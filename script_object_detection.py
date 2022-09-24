#!/home/users/justind/.conda/envs/tf_gpu/bin/
#!/usr/bin/env python
# coding: utf-8
def main(date,flag):
    
    ############################################################################
    #                                                                          #
    #   First step: Get all of the GPU information and allow memory growth     #
    #               this script differs from plot_object_detection because     #
    #               it uses the 2nd gpu, it allows no command line arguments   #
    #                                                                          #
    ############################################################################
    import os
    import sys
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging (1)]
    os.environ["CUDA_VISIBLE_DEVICES"]="1"	    # Use 2nd GPU
    import pathlib
    import tensorflow as tf
    from datetime import datetime
    from pascal_voc_writer import Writer
    import time
    from object_detection.utils import label_map_util
    from object_detection.utils import config_util
    from object_detection.builders import model_builder
    import numpy as np
    from PIL import Image
    import warnings
    tf.get_logger().setLevel('ERROR')           # Suppress TensorFlow logging (2)

    gpus = tf.config.experimental.list_physical_devices('GPU')
    # Is allocating a set % of the gpu memory better than allowing growth?
    # Does growth even work correctly? 
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

    print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

    ############################################################################
    #                                                                          #
    #   Second step: Need to get the correct date format that was passed into  # 
    #   main (MM-DD-YYYY was passed in, we need YYYY-MM-DD for the raw image)  #
    #                                                                          #
    ############################################################################
    IMAGE_PATHS = [] # list of raw images
    MISSING_RAW_IMAGES = []

    # get the correct formatting of the raw image directories
    raw_year = date[6:10]
    raw_month = date[0:2]
    raw_day = date[3:5]
    raw_path = raw_year + "/" + raw_month + "/" + raw_day + "/"

    temp_image_dir = "/raid/AoT/sage/000048B02D15BC7D/bottom/" + raw_path # YYYY/MM/DD
    xml_output_dir = "/raid/AoT/image_label_xmls/" + date + "/" # directory is created if it does not exist later MM-DD-YYYY

    if not os.path.isdir(temp_image_dir):
        print("Raw image directory does not exist:", temp_image_dir, ", terminating program")
        return

    if not os.path.isdir(xml_output_dir): # creation of xml output directory if it does not exist
        os.mkdir(xml_output_dir)


    ############################################################################
    #                                                                          #
    #   Third Step: Check for corrupted image data, append raw images to list, #
    #   load of all of the model and labels and check for success              #
    #                                                                          #
    ############################################################################
    # Nested loop to check to see if the image is corrupted, if not, append that image to the IMAGE_PATHS list
    for filename in os.listdir(temp_image_dir): # raw image directory
        for picture in os.listdir(temp_image_dir + filename):
            # print("Pic: ", picture)
            if os.path.getsize((os.path.join(temp_image_dir + filename, picture))) <= 0:
                print("Corrupted file found, terminating object detection for this day")
                return 
            IMAGE_PATHS.append(os.path.join(temp_image_dir + filename, picture))

    # Download the model
    def download_model(model_name, model_date):
        base_url = 'http://download.tensorflow.org/models/object_detection/tf2/'
        model_file = model_name + '.tar.gz'
        model_dir = tf.keras.utils.get_file(fname=model_name,
                                            origin=base_url + model_date + '/' + model_file,
                                            untar=True)
        return str(model_dir)

    # Download labels file
    def download_labels(filename):
        base_url = 'https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/data/'
        label_dir = tf.keras.utils.get_file(fname=filename,
                                            origin=base_url + filename,
                                            untar=False)
        label_dir = pathlib.Path(label_dir)
        return str(label_dir)
    
    # Get all of the information for the Model and its Labels
    MODEL_DATE = '20200711'
    #MODEL_NAME = 'efficientdet_d4_coco17_tpu-32'
    #Original model below - takes longer and has a bit less accuracy, MODEL_DATE is the same for both models
    MODEL_NAME = 'centernet_hg104_1024x1024_coco17_tpu-32'
    PATH_TO_MODEL_DIR = download_model(MODEL_NAME, MODEL_DATE)
    # LABEL_FILENAME holds all the classes, their names, IDs and descriptions: LABEL ID 1 = person
    LABEL_FILENAME = 'mscoco_label_map.pbtxt'
    PATH_TO_LABELS = download_labels(LABEL_FILENAME)
    PATH_TO_CFG = PATH_TO_MODEL_DIR + "/pipeline.config"
    PATH_TO_CKPT = PATH_TO_MODEL_DIR + "/checkpoint"

    # Check to see if the model loaded correctly or not
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

    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

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
        # We're only interested in the first num_detections.f
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

            return file_date, True    #return true if the file was processed

        return file_date, False   #return false since the file was not processed

    ############################################################################
    #                                                                          #
    #   Fourth Step: Create an xml directory based on the input date if need,  #
    #   run write_label_xmls() to create the xmls for that day                 #
    #                                                                          #
    ############################################################################

   
    # Loop to create xmls
    for image_path in IMAGE_PATHS:# add the .xml files into the correct directories
        xml_path = xml_output_dir + os.path.basename(str(image_path)).replace("jpg", "xml")
        #print(xml_path)
        if flag == 0: # flag passed in from missing days -x that will NOT overwrite xmls
            if os.path.exists(xml_path): # do not create new files if they exist 
                continue
            else:
                write_label_xmls(detection_model, image_path)
        else: # flag is 1 meaning missing days -x WILL overwrite xmls
            write_label_xmls(detection_model, image_path)
    
   
if __name__=='__main__':
    main()

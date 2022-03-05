# Sage Pedestrian
Pedestrian tracking with data from NSF Sage Project
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**env.yml:** Conda environment to run scripts  
**plot_object_detection.py:** Run the images through the object detection model and spits out an xml file containing the results  
**pedestrian_detection.py:** Parse xml files and track people in the photo using re-id  
**plot_lines.py:** Parse .csv output files containing coordinates of people and draw paths on top of an image 

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Students:** Justin Derus, Wesley Kwiecinski                   
**Mentors:** Pratool Bharti, Michael Papka            
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Useful Sources:**  
Tutorial to create conda env: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment
Open CV Image Writing: https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html (Python is below c++)  
Open CV Line Drawing Documentation: https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html  
Object Detection Tutorial: https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_saved_model.html  
Deep Re-id: https://github.com/KaiyangZhou/deep-person-reid  

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**STEPS TO GETTING THE CODE UP AND RUNNING (on hartley):**

0) Clone this github repo
1) Create and activate a new [conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment) using the provided env.yml file (If conda throws errors that is okay, just activate the environment and keep going.)
2) Clone [the deep-person-reid repo](https://github.com/KaiyangZhou/deep-person-reid) into this cloned repository, and follow the necessary steps for installation
4) Make sure that the .xml files for the day you run exist in this directory /raid/AoT/image_label_xmls/ 
5) Run the pedestrian_detection script following this format: "python pedestrian_detection.py [hour_min] [hour_max] [date1, date2, ...]"
  - Where hours are optional, dateN = yyyy/mm/dd
6) The output of the pedestrian_detection.py script will be found in /raid/AoT/image_label_xmls/crosswalk_detections/

**TROUBLESHOOTING)**
 - If the code refuses to use the gpu, try adding this to your .bashrc script in your home directory
  export CUDA_VISIBLE_DEVICES=0
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/[user]/.conda/envs/tf_gpu/lib
  export PYTHONPATH=$PYTHONPATH:/home/[user]/work/models
  
 - "ModuleNotFoundError: No module named 'torchreid'" -> Double check the deep-reid path at the top of pedestrian_detection.py if you get this error
    - For any "ModuleNotFoundError", "pip install [module_name]" will usually do the trick.
    - In the case of cv2, try pip install opencv-python

 - If you are running a specified day on the plot_object_detection.py script and want it to run in the background, follow the steps commented at the top of that file

![alt text](https://github.com/ddiLab/SagePedestrian/blob/main/sample_images/line_result.JPG?raw=true)

*This material is based upon work supported by the National Science Foundation under Grant No. OAC 1935984.*

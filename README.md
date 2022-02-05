# Sage Pedestrian
Pedestrian tracking with data from NSF Sage Project

*What files are here and why?*  
**plot_object_detection.py:** Run the images through the object detection model and spits out an xml file containing the results  
**pedestrian_detection.py:** Parse xml files and track people in the photo using re-id  
**plot_lines.py:** Parse .csv output files containing coordinates of people and draw paths on top of an image  
**env.yml:** Conda environment to run scripts  

**Students:** Justin Derus, Wesley Kwiecinski
**Mentors:** Pratool Bharti, Michael Papka

**Useful Sources:**  
Open CV Image Writing: https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html (Python is below c++)  
Open CV Line Drawing Documentation: https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html  
Object Detection Tutorial: https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_saved_model.html  
Deep Re-id: https://github.com/KaiyangZhou/deep-person-reid  

*This material is based upon work supported by the National Science Foundation under Grant No. OAC 1935984.*

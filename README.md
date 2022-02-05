# Sage Pedestrian
Pedestrian tracking with data from NSF Sage Project

**env.yml:** Conda environment to run scripts  
**plot_object_detection.py:** Run the images through the object detection model and spits out an xml file containing the results  
**pedestrian_detection.py:** Parse xml files and track people in the photo using re-id  
**plot_lines.py:** Parse .csv output files containing coordinates of people and draw paths on top of an image 


- !!!plot_object_detection.py and pedestrian_detection.py both have dates and directories hard coded, if running a new day these must be changed!!! (temporary)
- see below for where to change these dates/directories

**Students:** Justin Derus, Wesley Kwiecinski
**Mentors:** Pratool Bharti, Michael Papka

**Useful Sources:**  
Open CV Image Writing: https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html (Python is below c++)  
Open CV Line Drawing Documentation: https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html  
Object Detection Tutorial: https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_saved_model.html  
Deep Re-id: https://github.com/KaiyangZhou/deep-person-reid  


plot_object_detection.py changes:



![alt text](https://github.com/ddiLab/SagePedestrian/blob/main/sample_images/plot_object_detection1.PNG?raw=true)

pedestrian_detection.py changes:



![alt text](https://github.com/ddiLab/SagePedestrian/blob/main/sample_images/pedestrian_detection1.PNG?raw=true)

![alt text](https://github.com/ddiLab/SagePedestrian/blob/main/sample_images/pedestrian_detection2.PNG?raw=true)
![alt text](https://github.com/ddiLab/SagePedestrian/blob/main/sample_images/pedestrian_detection3.PNG?raw=true)




![alt text](https://github.com/ddiLab/SagePedestrian/blob/main/sample_images/line_result.jpg?raw=true)

*This material is based upon work supported by the National Science Foundation under Grant No. OAC 1935984.*

# Introduction
If you have a ready model and you want to train a new model, you can have the model do some of the labeling. That, you can save time from tagging.
# Get Started
1. To clone this project to your own device:
    ```
    git clone https://github.com/yunuserdemakpinar/Detectron2Cvat.git
    ```
2. Throw the predictions txt files and untagged photos from Detectron2 to the Detectron folder in the project file. (For each photo, the predictions name and the photo's name must be the same and a number.)
3. You have to open Detectron2Cvat.py and use the Detectron2Cvat(projectName, labelNames, taggingPeopleCount) function. Parameters you need to know to use this function:
    1. projectName: Project name to appear in CVAT.
    2. labelNames: List of label names starting from id 0.
    3. taggingPeopleCount: Number of people to tag in CVAT.
4. Now you can upload cvat.zip to [CVAT](https://cvat.org/projects) from "Create from backup" under the "Create Project".
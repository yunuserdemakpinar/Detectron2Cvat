from copy import deepcopy
import re, os, json, random, shutil, zipfile

def CreateFolders(projectName):
    os.mkdir(projectName)
    os.chdir(projectName)
    os.mkdir("task_0")
    os.chdir("task_0")
    os.mkdir("data")
    os.chdir("../..")

def CreateProjectJson(projectName, labelNames):
    file = open("JsonFiles/projectTemplate.json")
    projectJson = json.loads(file.read())
    file.close()
    projectJson["name"] = projectName
    for i in range(len(labelNames) - 1, -1, -1):
        color = "#" + "%06x" % random.randint(0, 0xFFFFFF)
        projectJson["labels"] += [{"name":labelNames[i],"color":color,"attributes":[]}]
    file = open(projectName + "/project.json", "w")
    file.write(json.dumps(projectJson))
    file.close()

def GetImageCount():
    imageCount = 0
    detectrons = os.listdir("Detectron")
    for i in range(len(detectrons)):
        if detectrons[i][len(detectrons[i]) - 3:] == "txt":
            imageCount += 1
    return imageCount

def CreateTaskJson(projectName, taggingPeopleCount, imageCount):
    file = open("JsonFiles/taskTemplate.json")
    taskJson = json.loads(file.read())
    file.close()
    file = open(projectName + "/project.json", "r")
    projectJson = json.loads(file.read())
    file.close()
    taskJson["name"] = projectName
    taskJson["labels"] = projectJson["labels"]
    taskJson["data"]["stop_frame"] = imageCount - 1
    remain = imageCount % taggingPeopleCount
    newImageCount = imageCount - remain
    jobs = []
    for i in range(taggingPeopleCount):
        startFrame = i * newImageCount / taggingPeopleCount
        stopFrame = (i + 1) * newImageCount / taggingPeopleCount - 1
        if i < remain:
            stopFrame += i + 1
            if i != 0:
                startFrame += i
        else:
            startFrame += remain
            stopFrame += remain
        taskJson["jobs"] += [{"start_frame": int(startFrame), "stop_frame": int(stopFrame), "status": "annotation"}]
        jobs += [stopFrame]
    file = open(projectName + "/task_0/task.json", "w")
    file.write(json.dumps(taskJson))
    file.close()
    return jobs

def CreateAnnotationsJson(projectName, labelNames, jobs):
    imageCount = -1
    file = open("JsonFiles/annotationsTemplate.json", "r")
    annotationsTemplate = json.loads(file.read())
    file.close()
    annotations = deepcopy(annotationsTemplate)
    annotationsJson = json.loads("[]")
    jobCounter = 0
    detectrons = os.listdir("Detectron")
    for i in range(len(detectrons)):
        if detectrons[i][len(detectrons[i]) - 3:] == "txt":
            try:
                detectronFile = open("Detectron/" + detectrons[i], "r")
                detectronText = detectronFile.read().replace("\n", "")
                detectronFile.close()
                labelCount = int(re.findall("\d+", re.findall("num_instances=\d+", detectronText)[0])[0])
                pointsList = re.findall("\[\s*\d+\.[^,]*,\s*\d+\.[^,]*,\s*\d+\.[^,]*,\s*\d+\.[^,]*\]", re.findall("pred_boxes:.*\]\]", detectronText)[0])
                for j in range(labelCount):
                    points = []
                    points += re.findall("\d+\.[^,\]]*", pointsList[j])
                    for k in range(4):
                        points[k] = float(points[k])
                    label = int(re.findall("\d+", re.findall("pred_classes:.*\],", detectronText)[0])[j])
                    annotations["shapes"] += [{"type":"rectangle","occluded":False,"z_order":0,"rotation":0.0,"points":[points[0],points[1],points[2],points[3]],"frame":imageCount,"group":0,"source":"manual","attributes":[],"label":labelNames[label]}]
            except:
                continue
            else:
                if imageCount == jobs[jobCounter]:
                    jobCounter += 1
                    annotationsJson += [annotations]
                    annotations = deepcopy(annotationsTemplate)
                imageCount += 1
                images = os.listdir("Detectron")
                for j in images:
                    if (detectrons[i][:len(detectrons[i]) - 4] == j[:len(j) - 4] and j[len(j) - 3:] != "txt"):
                        shutil.copy("Detectron/" + j, projectName + "/task_0/data/")
                        os.rename(projectName + "/task_0/data/" + j, projectName + "/task_0/data/" + str(i + 1000) + ".jpg")
    file = open(projectName + "/task_0/annotations.json", "w")
    file.write(json.dumps(annotationsJson))
    file.close()

def CreateZipFile(projectName):
    os.chdir(projectName)
    with zipfile.ZipFile("../cvat.zip", "a") as zip:
        zip.write("project.json")
        zip.write("task_0")
        zip.write("task_0/annotations.json")
        zip.write("task_0/task.json")
        zip.write("task_0/data")
        images = os.listdir("task_0/data")
        for i in images:
            zip.write("task_0/data/" + i)
    os.chdir("..")
    shutil.rmtree(projectName)

def Detectron2Cvat(projectName, labelNames, taggingPeopleCount):
    if os.path.exists("cvat.zip") and os.path.isfile("cvat.zip"):
        os.remove("cvat.zip")
    CreateFolders(projectName)
    CreateProjectJson(projectName, labelNames)
    imageCount = GetImageCount()
    jobs = CreateTaskJson(projectName, taggingPeopleCount, imageCount)
    CreateAnnotationsJson(projectName, labelNames, jobs)
    CreateZipFile(projectName)

Detectron2Cvat("ProjectName", ["A", "B", "C"], 1)
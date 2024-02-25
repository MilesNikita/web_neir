from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import SuspiciousOperation
import cv2
import numpy as np
import os
import threading
import base64
from io import BytesIO
from PIL import Image

CONFIDENCE = 0.5
SCORE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.5
NMSThreshold = 0.3

config_path = 'yolov3.cfg'
weights_path = 'yolov3.weights'
labels_path = 'coco.names'
net = cv2.dnn.readNetFromDarknet(config_path, weights_path)

def login_page(request):
    return render(request, 'login.html')

def neural_network(request):
    return render(request, 'neural_network.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('neural_network') 
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'login.html')

def run_neural_network(request):
    if request.method == 'POST':
        selected_input_type = request.POST.get('input_type')
        if selected_input_type == 'image':
            image_file = request.FILES.get('image')
            if image_file:
                try:
                    save_path = os.path.join(settings.MEDIA_ROOT, 'temp_image.jpg')
                    with open(save_path, 'wb') as f:
                        for chunk in image_file.chunks():
                            f.write(chunk)
                    processed_image_path = process_image(save_path)
                    if processed_image_path:
                        processed_image_url = os.path.join(settings.MEDIA_URL, 'processed_image.jpg')
                        return JsonResponse({'status': 'success', 'processed_image': processed_image_url})
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Error processing image'})
                except SuspiciousOperation:
                    return JsonResponse({'status': 'error', 'message': 'Invalid operation'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Image not uploaded'})
        elif selected_input_type == 'video':
            video_file = request.FILES.get('video')
            if video_file:
                try:
                    save_path = os.path.join(settings.MEDIA_ROOT, 'temp_video.mp4')
                    with open(save_path, 'wb') as f:
                        for chunk in video_file.chunks():
                            f.write(chunk)
                    processed_video_path = process_video(save_path)
                    if processed_video_path:
                        processed_video_url = os.path.join(settings.MEDIA_URL, 'processed_video.mp4')
                        return JsonResponse({'status': 'success', 'processed_video': processed_video_url})
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Error processing video'})
                except SuspiciousOperation:
                    return JsonResponse({'status': 'error', 'message': 'Invalid operation'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Video not uploaded'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method or input type'})

image_processing_lock = threading.Lock()

def process_image(image_path):
    labels = open(labels_path).read().strip().split("\n")
    colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")
    with image_processing_lock:
        image = cv2.imread(image_path)
        if image is None:
            return None
        h, w = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        ln = net.getLayerNames()
        try:
            ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        except IndexError:
            ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
        layer_outputs = net.forward(ln)
        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > CONFIDENCE:
                    box = detection[:4] * np.array([w, h, w, h])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    color = [int(c) for c in colors[class_id]]
                    cv2.rectangle(image, (x, y), (x + width, y + height), color, 2)
                    text = "{}: {:.4f}".format(labels[class_id], confidence)
                    cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        processed_image_path = os.path.join(settings.MEDIA_ROOT, 'processed_image.jpg')
        cv2.imwrite(processed_image_path, image)
    return processed_image_path if os.path.isfile(processed_image_path) else None

def process_video(video_path):
    labels = open(labels_path).read().strip().split('\n')
    np.random.seed(10)
    COLORS = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")
    outputLayer = net.getLayerNames()
    try:
        outputLayer = [outputLayer[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    except IndexError:
        outputLayer = [outputLayer[i - 1] for i in net.getUnconnectedOutLayers()]
    video = cv2.VideoCapture(video_path)
    writer = None
    (W, H) = (None, None)
    try:
        prop = cv2.CAP_PROP_FRAME_COUNT
        total = int(video.get(prop))
    except:
        print("Could not determine no. of frames in video")
    count = 0
    while True:
        (ret, frame) = video.read()
        if not ret:
            break
        if W is None or H is None:
            (H,W) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB = True, crop = False)
        net.setInput(blob)
        layersOutputs = net.forward(outputLayer)
        boxes = []
        confidences = []
        classIDs = []
        for output in layersOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > CONFIDENCE:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY,  width, height) = box.astype('int')
                    x = int(centerX - (width/2))
                    y = int(centerY - (height/2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
                    detectionNMS = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE, NMSThreshold)
                    if(len(detectionNMS) > 0):
                        for i in detectionNMS.flatten():
                            (x, y) = (boxes[i][0], boxes[i][1])
                            (w, h) = (boxes[i][2], boxes[i][3])
                            color = [int(c) for c in COLORS[classIDs[i]]]
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                            text = '{}: {:.4f}'.format(labels[classIDs[i]], confidences[i])
                            cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            if writer is None:
                                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                                writer = cv2.VideoWriter(os.path.join(settings.MEDIA_ROOT,'output.mp4'), fourcc, 30, (frame.shape[1], frame.shape[0]), True)
                    if writer is not None:
                        writer.write(frame)
                        count = count + 1
    writer.release()
    video.release()
    return writer if os.path.isfile(writer) else None
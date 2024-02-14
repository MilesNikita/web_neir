from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import cv2
import numpy as np
import os
import threading

CONFIDENCE = 0.5
SCORE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.5

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
        selected_model = request.POST.get('model')
        selected_input_type = request.POST.get('input_type')
        if selected_model == 'model1' and selected_input_type == 'image':
            image_file = request.FILES.get('image')
            if image_file:
                save_path = os.path.join(settings.MEDIA_ROOT, 'temp_image.jpg')
                with open(save_path, 'wb') as f:
                    for chunk in image_file.chunks():
                        f.write(chunk)
                processed_image_path = process_image(save_path)
                return JsonResponse({'status': 'success', 'processed_image': processed_image_path})
            else:
                return JsonResponse({'status': 'error', 'message': 'Изображение не было загружено'})
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

image_processing_lock = threading.Lock()

def process_image(image_path):
    config_path = "yolov3.cfg"
    weights_path = "yolov3.weights"
    labels = open("coco.names").read().strip().split("\n")
    colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")
    with image_processing_lock:
        image = cv2.imread(image_path)
        h, w = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
        net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
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
        processed_image_path = "processed_image.jpg"
        cv2.imwrite(processed_image_path, image)
    return processed_image_path
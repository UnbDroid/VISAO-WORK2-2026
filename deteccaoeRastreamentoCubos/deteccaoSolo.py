import apriltag
import cv2
import numpy as np

video = cv2.VideoCapture(3)
print("Câmera abriu?", video.isOpened())
ok, frame = video.read()
print("Frame capturado?", ok)

options = apriltag.DetectorOptions(families="tag36h11")
detector = apriltag.Detector(options)

video = cv2.VideoCapture(3)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

results = detector.detect(gray)

# parâmetros da câmera
# [fx, fy, cx, cy]
camera_params = [1121.40, 118.81, 649.17, 364.85]
tag_size = 0.04  # 4 centímetros

for r in results:
    # obter a pose completa usando os parâmetros da câmera e tamanho da tag
    pose, init_error, final_error = detector.detection_pose(r, camera_params, tag_size)
    
    print("Matriz de Pose Completa:\n", pose)
    
    # vetor de translação (X, Y, Z)
    x = pose[0][3]
    y = pose[1][3]
    z = pose[2][3] # Distância linear da câmera até a tag
    
    print(f"Cubo detectado a: X={x:.2f}m, Y={y:.2f}m, Z={z:.2f}m de distância")
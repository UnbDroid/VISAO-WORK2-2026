import cv2
import sys
from pupil_apriltags import Detector
from random import randint 
import numpy as np

nome_tracker = "CSRT"
tracker = cv2.TrackerCSRT_create()  
video = cv2.VideoCapture(3)

print("Câmera abriu?", video.isOpened())

if not video.isOpened():
    print('Não foi possível carregar o vídeo')
    sys.exit() 

# DroidCam = app de sincronixação da câmera do celular da Lelê
print("Aguardando o DroidCam sincronizar...")
for i in range(30):
    ok, frame = video.read()

# Agora sim pegamos um frame válido e limpo
ok, frame = video.read()

if not ok:
    print('Não foi possível ler o arquivo de vídeo')
    sys.exit() 


class ColorDetector:

    def __init__(self):
        pass

    def detect_color(self, roi):

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # vermelho
        red_lower = np.array([0,120,70])
        red_upper = np.array([10,255,255])

        # verde
        green_lower = np.array([40,50,50])
        green_upper = np.array([80,255,255])

        # azul
        blue_lower = np.array([100,150,0])
        blue_upper = np.array([140,255,255])

        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)

        red_pixels = red_mask.sum()
        green_pixels = green_mask.sum()
        blue_pixels = blue_mask.sum()

        if red_pixels > green_pixels and red_pixels > blue_pixels:
            return "red"

        elif green_pixels > red_pixels and green_pixels > blue_pixels:
            return "green"

        elif blue_pixels > red_pixels and blue_pixels > green_pixels:
            return "blue"

        return "unknown"

class AprilTagDetector:
    def __init__(self):
        # Sintaxe para versões mais antigas do OpenCV
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
        self.parameters = cv2.aruco.DetectorParameters()

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Nas versões antigas, a detecção é chamada diretamente de cv2.aruco
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, self.dictionary, parameters=self.parameters)
        tags = []

        if ids is not None:
            for i in range(len(ids)):
                c = corners[i][0]
                cx = int((c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4)
                cy = int((c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4)

                tag_data = {
                    "id": ids[i][0],
                    "center": (cx, cy),
                    "corners": c
                }
                tags.append(tag_data)

        return tags

class CubeDetector:
    def __init__(self, color_detector):
        self.color_detector = color_detector

    def detect_cubes(self, frame, tags):
        h, w = frame.shape[:2]

        # SE NÃO ACHAR NENHUMA TAG, AVISA QUE FALHOU
        if len(tags) == 0:
            return None 

        for tag in tags:
            
            cx = int(tag["center"][0])
            cy = int(tag["center"][1])

            size = 40

            x1 = max(cx - size, 0)
            x2 = min(cx + size, w)

            y1 = max(cy - size, 0)
            y2 = min(cy + size, h)

            roi = frame[y1:y2, x1:x2]
            color = self.color_detector.detect_color(roi)

            if cx < w * 0.33:
                position = "left"
            elif cx > w * 0.66:
                position = "right"
            else:
                position = "center"

            # O TAMANHO CORRETO DA CAIXA (Largura e Altura do quadradinho)
            largura_caixa = x2 - x1
            altura_caixa = y2 - y1
            
            bbox_correta = (x1, y1, largura_caixa, altura_caixa)
            
            # Retorna a caixa do primeiro cubo que ele achar e sai da função
            return bbox_correta 


# --- INICIALIZANDO O RASTREADOR COM SEGURANÇA ---

bbox = CubeDetector(ColorDetector()).detect_cubes(frame, AprilTagDetector().detect(frame))

while True:
    cv2.imshow('Tracking', frame)
    if cv2.waitKey(1) & 0XFF == 27:
        break

# Verifica se a função acima devolveu "None" (ou seja, não achou tag no começo)
if bbox is None:
    print("ERRO: Nenhuma AprilTag encontrada no primeiro frame do vídeo.")
    sys.exit()
else: 
    print("AprilTag encontrada! Iniciando rastreamento...")

# Se chegou aqui, é porque achou a caixa!
ok = tracker.init(frame, bbox)

colors = (randint(0, 255), randint(0, 255), randint(0, 255))
#print(colors)

while True:
    ok, frame = video.read()
    if not ok:
        break

    print("teste")

    # https://docs.opencv.org/master/dc/d71/tutorial_py_optimization.html
    timer = cv2.getTickCount()
    ok, bbox = tracker.update(frame)
    #print(ok, bbox)

    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    if ok:
        (x, y, w, h) = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), colors, 2, 1)
    else:
        cv2.putText(frame, 'Falha no rastreamento', (100, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 255), 2)

    cv2.putText(frame, nome_tracker + ' Tracker', (100, 20),
                cv2.FONT_HERSHEY_SIMPLEX, .75, (50, 170, 50), 2)

    cv2.putText(frame, 'FPS: ' + str(int(fps)), (100, 50),
                cv2.FONT_HERSHEY_SIMPLEX, .75, (50, 170, 50), 2)

    cv2.imshow('Tracking', frame)
    if cv2.waitKey(1) & 0XFF == 27:
        break
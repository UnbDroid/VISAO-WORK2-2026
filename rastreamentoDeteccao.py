import cv2
import sys
import apriltag
from random import randint 
import numpy as np

# INICIALIZAÇÃO
nome_tracker = "CSRT"
tracker = cv2.TrackerCSRT_create()  
video = cv2.VideoCapture(3)

fps = 0

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

# CLASSES DE DETECÇÃO   
class AprilTagDetector:
    def __init__(self):
        # usando biblioteca apriltag nativa
        self.options = apriltag.DetectorOptions(families="tag36h11")
        self.detector = apriltag.Detector(self.options)

        # parâmetros da câmera e tamanho da tag
        self.camera_params = [1121.40, 118.81, 649.17, 364.85]  # [fx, fy, cx, cy]
        self.tag_size = 0.04  # 4 centímetros

    def detect(self, frame):
        if frame is None:
            return []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = self.detector.detect(gray)
        tags = []

        for r in results:
            # obter a pose completa usando os parâmetros da câmera e tamanho da tag
            pose, init_error, final_error = self.detector.detection_pose(r, self.camera_params, self.tag_size)
            
            # vetor de translação (X, Y, Z)
            x_m = pose[0][3]
            y_m = pose[1][3]
            z_m = pose[2][3]

            tag_data = {
                "id": r.tag_id,
                "center": (int(r.center[0]), int(r.center[1])),
                "pose_3d": (x_m, y_m, z_m)
            }
            tags.append(tag_data)

        return tags

class CubeDetector:
    def __init__(self, color_detector=None):
        self.color_detector = color_detector

    def detect_cubes(self, frame, tags):
        # SE NÃO ACHAR NENHUMA TAG, AVISA QUE FALHOU
        if frame is None or len(tags) == 0:
            return None 

        h, w = frame.shape[:2]

        for tag in tags:
            cx, cy = tag["center"]
            size = 50

            x1 = max(cx - size, 0)
            x2 = min(cx + size, w)
            y1 = max(cy - size, 0)
            y2 = min(cy + size, h)
        
            # O TAMANHO CORRETO DA CAIXA (Largura e Altura do quadradinho)
            largura_caixa = x2 - x1
            altura_caixa = y2 - y1
            
            bbox_correta = (x1, y1, largura_caixa, altura_caixa)
            
            # retorna a bbox do primeiro cubo e os dados 3D dele
            return bbox_correta, tag["pose_3d"]


# INICIALIZANDO O RASTREADOR
tag_detector = AprilTagDetector()
cube_detector = CubeDetector()
colors = (randint(0, 255), randint(0, 255), randint(0, 255))

'''resultado = cube_detector.detect_cubes(frame, tag_detector.detect(frame))

if resultado is None:
    print("Nenhuma AprilTag encontrada no primeiro frame do vídeo. Tentará detectar no loop.")
    rastreando = False
else:
    bbox, pose_3d = resultado
    tracker.init(frame, bbox)
    rastreando = True
    print(f"Apriltag encontrada! Cubo inicial em: X={pose_3d[0]:.2f}m, Y={pose_3d[1]:.2f}m, Z={pose_3d[2]:.2f}m")

colors = (randint(0, 255), randint(0, 255), randint(0, 255))
'''

# LOOP PRINCIPAL
while True:
    ok, frame = video.read()
    if not ok or frame is None:
        break

    # registra o tempo incial do frame
    timer = cv2.getTickCount()

    # Detecta as tags no frame atual
    tags_encontradas = tag_detector.detect(frame)
    resultado = cube_detector.detect_cubes(frame, tags_encontradas)

    if resultado is not None:
        # se encontrou a tag, desenha a caixa e mostra a distância 3D
        bbox, pose_3d = resultado
        (x, y, w, h) = [int(v) for v in bbox]
        
        # desenha o retângulo ao redor do cubo
        cv2.rectangle(frame, (x, y), (x + w, y + h), colors, 2, 1)
        
        # mostra as coordenadas 3D na tela e no terminal
        x_m, y_m, z_m = pose_3d
        cv2.putText(frame, f"X:{x_m:.2f}m Y:{y_m:.2f}m Z:{z_m:.2f}m", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        cv2.putText(frame, "STATUS: RASTREANDO", (100, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, .75, (50, 170, 50), 2)
    else:
        # se não encontrou nenhuma tag, avisa na tela e continua procurando no próximo frame
        cv2.putText(frame, "STATUS: BUSCANDO CUBO...", (100, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 255), 2)

    # cálculo de FPS
    dt = (cv2.getTickCount() - timer) / cv2.getTickFrequency()
    if dt > 0:
        fps = 1.0 / dt

    cv2.putText(frame, 'FPS: ' + str(int(fps)), (100, 50),
                cv2.FONT_HERSHEY_SIMPLEX, .75, (255, 255, 255), 2)

    cv2.imshow('Tracking', frame)
    if cv2.waitKey(1) & 0XFF == 27: # Esc para sair
        break

video.release()
cv2.destroyAllWindows()
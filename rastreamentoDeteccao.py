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

# CLASSE DE DETECÇÃO   
class AprilTagDetector:
    def __init__(self):
        # usando biblioteca apriltag nativa
        self.options = apriltag.DetectorOptions(families="tag36h11")
        self.detector = apriltag.Detector(self.options)

        # parâmetros da câmera e tamanho da tag
        self.camera_params = [1121.40, 118.81, 649.17, 364.85]  # [fx, fy, cx, cy]
        self.tag_size = 0.06  # 6 centímetros

    def detect(self, frame):
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
        h, w = frame.shape[:2]

        # SE NÃO ACHAR NENHUMA TAG, AVISA QUE FALHOU
        if len(tags) == 0:
            return None 

        for tag in tags:
            
            cx, cy = tag["center"]

            size = 80

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

resultado = cube_detector.detect_cubes(frame, tag_detector.detect(frame))

if resultado is None:
    print("Nenhuma AprilTag encontrada no primeiro frame do vídeo. Tentará detectar no loop.")
    rastreando = False
else:
    bbox, pose_3d = resultado
    tracker.init(frame, bbox)
    rastreando = True
    print(f"Apriltag encontrada! Cubo inicial em: X={pose_3d[0]:.2f}m, Y={pose_3d[1]:.2f}m, Z={pose_3d[2]:.2f}m")

colors = (randint(0, 255), randint(0, 255), randint(0, 255))


# LOOP PRINCIPAL
while True:
    ok, frame = video.read()
    if not ok:
        break

    timer = cv2.getTickCount()

    if rastreando:
        # se estiver rastreando, atualiza o tracker CSRT
        ok_tracker, bbox = tracker.update(frame)

        if ok_tracker:
            (x, y, w, h) = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y+ h), colors, 2, 1)

            # rodando a detecção de pose em background p/ manter a distãncia atualizada
            tags = tag_detector.detect(frame)
            if tags:
                x_m, y_m, z_m = tags[0]["pose_3d"]
                cv2.putText(frame, f"Dist: {z_m:.2f}m", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                print(f"Rastreando - Cubo a: X={x_m:.2f}m, Y={y_m:.2f}m, Z={z_m:.2f}m")
            else:
                # se o tracker falhou, desativa o modo de rastreamento para forçar a redetecção
                rastreando = False
                print("Rastreamento perdido. Tentando redetectar a AprilTag...")

        if not rastreando:
            # se não estiver rastreando (ou perdeu), tenta detectar a tag novamente
            resultado = cube_detector.detect_cubes(frame, tag_detector.detect(frame))

            if resultado is not None:
                bbox, pose3d =  resultado
                # reinicializa o tracker com a nova posição encontrada
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, bbox)
                rastreando = True
                print(f"Tag recuperada! Novo ponto: X={pose_3d[0]:.2f}m, Y={pose_3d[1]:.2f}m, Z={pose_3d[2]:.2f}m")
            else:
                cv2.putText(frame, 'Buscando AprilTag...', (100, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 255), 2)
                
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
                
        # textos informativos n tela!!!!!!
        cv2.putText(frame, nome_tracker + ' Tracker', (100, 20),
                cv2.FONT_HERSHEY_SIMPLEX, .75, (50, 170, 50), 2)

    cv2.putText(frame, 'FPS: ' + str(int(fps)), (100, 50),
                cv2.FONT_HERSHEY_SIMPLEX, .75, (50, 170, 50), 2)

    cv2.imshow('Tracking', frame)
    if cv2.waitKey(1) & 0XFF == 27: # Esc para sair
        break

video.release()
cv2.destroyAllWindows()
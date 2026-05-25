import cv2
import sys
from random import randint

from apriltag_detector import AprilTagDetector

class CubeDetector:

    def detect_cubes(self, frame, tags):

        h, w = frame.shape[:2] # altura, largura
        cubes = []

        for tag in tags:

            cx = int(tag["center"][0])
            cy = int(tag["center"][1])

            size = 40

            x = max(cx-size, 0)
            y = max(cy-size, 0)

            largura = min(size*2, w-x)
            altura = min(size*2, h-y)

            # posição na mesa
            if cx < w*0.33:
                position = "left"

            elif cx > w*0.66:
                position = "right"

            else:
                position = "center"

            cube = {
                "tag": tag["id"],
                "position": position,
                "bbox": (x, y, largura, altura)
            }

            cubes.append(cube)

        return cubes


# video:

video = cv2.VideoCapture("videos/walking.avi")

if not video.isOpened():
    print("Não foi possível abrir vídeo")
    sys.exit()

detector = CubeDetector()

#tracker = None
tracking = False # rastreando?

cor = (randint(0,255), randint(0,255), randint(0,255))

while True:
    ok, frame = video.read()

    if not ok:
        break


    # se estiver rastreando:
    if tracking:

        ok, bbox = tracker.update(frame)

        if ok:
            x,y,w,h = [int(v) for v in bbox]

            cv2.rectangle(frame, (x,y), (x+w,y+h), cor, 2)

            cv2.putText(frame,
                "Rastreando cubo", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)

        else:

            print("Perdeu rastreamento")
            tracking = False


    # se não estiver rastreando:

    else:
        tags = detector(frame) # tags detectadas pelo AprilTag

        cubes = detector.detect_cubes(frame, tags)

        if len(cubes)>0:

            cubo = cubes[0]
            bbox = cubo["bbox"]
            tracker = cv2.TrackerCSRT_create()
            tracker.init(frame, bbox)

            tracking = True

            print("Cubo encontrado:", cubo["tag"])

    cv2.imshow("Detecção + Rastreamento", frame)

    tecla = cv2.waitKey(1)

    if tecla == 27:
        break


video.release()
cv2.destroyAllWindows()
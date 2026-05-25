import cv2
import sys
from random import randint

tracker = cv2.TrackerCSRT_create() 
print(tracker)

#print(tracker)

video = cv2.VideoCapture(3)
if not video.isOpened():
    print('Não foi possível carregar o vídeo')
    sys.exit()

ok, frame = video.read()
if not ok:
    print('Não foi possível ler o arquivo de vídeo')
    sys.exit()

#print(ok)

bbox = cv2.selectROI(frame, False)
#print(bbox)

ok = tracker.init(frame, bbox)
#print(ok)

colors = (randint(0, 255), randint(0, 255), randint(0, 255))
#print(colors)

while True:
    ok, frame = video.read()
    if not ok:
        break

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

    cv2.putText(frame, str(tracker) + ' Tracker', (100, 20),
                cv2.FONT_HERSHEY_SIMPLEX, .75, (50, 170, 50), 2)

    cv2.putText(frame, 'FPS: ' + str(int(fps)), (100, 50),
                cv2.FONT_HERSHEY_SIMPLEX, .75, (50, 170, 50), 2)

    cv2.imshow('Tracking', frame)
    if cv2.waitKey(1) & 0XFF == 27:
        break
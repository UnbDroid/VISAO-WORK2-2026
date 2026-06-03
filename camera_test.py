import cv2

video = cv2.VideoCapture(3)
print("Câmera abriu?", video.isOpened())
ok, frame = video.read()
print("Frame capturado?", ok)

while True:

    ok, frame = video.read()
    if not ok:
        break

    cv2.imshow("frame", frame)
    k = cv2.waitKey(1) & 0XFF
    if k == 27:
        break

video.release()
import cv2

cap = cv2.VideoCapture(3)
print("Câmera abriu?", cap.isOpened())
ret, frame = cap.read()
print("Frame capturado?", ret)

while True:

    ok, frame = cap.read()
    if not ok:
        break

    cv2.imshow("frame", frame)
    k = cv2.waitKey(1) & 0XFF
    if k == 27:
        break

cap.release()
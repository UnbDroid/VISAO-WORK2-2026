import cv2
import sys


imagem=cv2.imread("fotofita.jpeg")
cv2.imshow("PEWPEWPEW", imagem)
cv2.waitKey(0)
cv2.imwrite("saidafotofita.jpeg", imagem)
(B,G,R)=imagem[0,0]
print(B,G,R) 
cv2.destroyAllWindows()
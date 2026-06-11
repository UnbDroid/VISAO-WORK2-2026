import cv2
import sys
import numpy as np

#Função para facilitar a escrita nas imagem
def escreve(img, texto, cor=(255,0,0)):
 fonte = cv2.FONT_HERSHEY_SIMPLEX
 cv2.putText(img, texto, (10,20), fonte, 0.5, cor, 0,
 cv2.LINE_AA)

imgColorida = cv2.imread('fotofita.jpeg') #Carregamento da imagem
#Se necessário o redimensioamento da imagem pode vir aqui.
#Passo 1: Conversão para tons de cinza
img = cv2.cvtColor(imgColorida, cv2.COLOR_BGR2GRAY)

#cv2.imshow("PEWPEWPEW", img)
#cv2.waitKey(0)
#cv2.imwrite("saidafotofita.jpeg", img)
suave = cv2.GaussianBlur(img, (7, 7), 0) # aplica blur
(T, bin) = cv2.threshold(suave, 160, 255, cv2.THRESH_BINARY)
(T, binI) = cv2.threshold(suave, 160, 255,
cv2.THRESH_BINARY_INV)

#Passo 4: Detecção de bordas com Canny
bordas = cv2.Canny(bin, 70, 150)

(lx, objetos, lx) = cv2.findContours(bordas.copy(),
 cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


escreve(img, "Imagem em tons de cinza", 0)
escreve(suave, "Suavizacao com Blur", 0)
escreve(bin, "Binarizacao com Metodo Otsu", 255)
escreve(bordas, "Detector de bordas Canny", 255)
temp = np.vstack([
np.hstack([img, suave]),
np.hstack([bin, bordas])
]) 


cv2.imshow("Quantidade de objetos: "+str(len(objetos)), temp)
cv2.waitKey(0)
imgC2 = imgColorida.copy()
cv2.imshow("Imagem Original", imgColorida)
48
cv2.drawContours(imgC2, objetos, -1, (255, 0, 0), 2)
escreve(imgC2, str(len(objetos))+" objetos encontrados!")
cv2.imshow("Resultado", imgC2)
cv2.waitKey(0)

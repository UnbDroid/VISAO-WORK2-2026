import cv2
import sys
import numpy as np
import math

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
(T, binI) = cv2.threshold(suave, 160, 255,cv2.THRESH_BINARY_INV)

#Passo 4: Detecção de bordas com Canny
bordas = cv2.Canny(bin, 70, 150)

objetos, _ = cv2.findContours(bordas.copy(), 
  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


imgResultado = imgColorida.copy() # cópia p/ desenhar os resultados finais

centros = []
listras_detectadas = 0
print(f"Contornos totais encontrados pelo Canny: {len(objetos)}")

for contorno in objetos:
    #calcula o perimetro do contorno
    perimetro = cv2.arcLength(contorno, True) # True significa que o contorno é fechado

    # approxPolyDP aproxima a forma geométrica
    # 0.04 (4% do perímetro) é uma tolerância comum para detectar retângulos
    aproximacao = cv2.approxPolyDP(contorno, 0.04 * perimetro, True)
   
    # se a aprox. tem 4 vertices, significa que temos um quadrilátero (uma lista da fita!!)
    # > 100 é um # > 100 é um filtro de área mínima p/ ignorar pequenos ruidos da imagemfiltro de área mínima p/ ignorar pequenos ruidos da imagem
    if len(aproximacao) == 4 and cv2.contourArea(contorno) > 100:
        listras_detectadas += 1     
     
    cv2.drawContours(imgResultado, [aproximacao], -1, (0, 255, 0), 2)

    print("F\n-> Listra #{listras_detectadas} detectada")
    print(F"Vértices:\n{aproximacao}")

    #encontrar o centro usando momentos da imagem
    M = cv2.moments(contorno)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        centros.append((cx, cy))

        cv2.circle(imgResultado, (cx, cy), 5, (255, 0, 0), -1)

        cor_bgr = imgColorida[cy, cx]
        print(F"Cor original no centro (BGR): {cor_bgr}")

# cálculo das distrâncias

#ordenando os centros da esquerda p/ direita p/ garantir que vai medir a distancia entre listras consecutivas
centros = sorted(centros, key = lambda ponto: ponto[0])

for i in range(len(centros) -1):
    p1 = centros[i]
    p2 = centros[ i + 1]

    # distância euclidiana: d = raiz((x2 - x1)^2 + (y2 - y1)^2)
    distancia = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    cv2.line(imgResultado, p1, p2, (0, 255, 255), 2)

    #calcula o ponto medio
    meio_x = int((p1[0] + p2[0]) / 2)
    meio_y = int((p1[1] + p2[1]) / 2)
    cv2.putText(imgResultado, f"{distancia:.1f}px", (meio_x, meio_y - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    print(F"Distância entre a listra {i + 1} e a listra {i + 2}: [ditância:2f] pixels")


print(img, "Imagem em tons de cinza", 0)
print(suave, "Suavizacao com Blur", 0)
print(bin, "Binarizacao com Metodo Otsu", 255)
print(bordas, "Detector de bordas Canny", 255)
temp = np.vstack([
np.hstack([img, suave]),
np.hstack([bin, bordas])
]) 


cv2.imshow("Quantidade de objetos: "+str(len(objetos)), temp)
cv2.waitKey(0)
imgC2 = imgColorida.copy()
cv2.imshow("Imagem Original", imgColorida)

cv2.drawContours(imgC2, objetos, -1, (255, 0, 0), 2)
escreve(imgC2, str(len(objetos))+" objetos encontrados!")
cv2.imshow("Resultado", imgC2)
cv2.waitKey(0)

cv2.imshow("Paredes Virtuais Identificadas", imgResultado)
cv2.waitKey(0)
cv2.destroyAllWindows()
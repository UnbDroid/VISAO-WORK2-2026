import cv2
import sys
import numpy as np
import math

#Função para facilitar a escrita nas imagem
def escreve(img, texto, cor=(255,0,0)):
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, texto, (10,20), fonte, 0.5, cor, 0, cv2.LINE_AA)

imgColorida = cv2.VideoCapture(2, cv2.CAP_V4L2)
print("Câmera abriu?", imgColorida.isOpened())

if not imgColorida.isOpened():
    print('Não foi possível carregar o vídeo')
    sys.exit()

ok, frame = imgColorida.read()
if not ok:
    print("Não foi possível ler o aquivo de vídeo")
    sys.exit()

ultimo_temp = None
ultimo_objetos = []

while True:
    ok, frame = imgColorida.read()
    if not ok or frame is None:
        break

    #imgColorida = cv2.imread('fotofita.jpeg') #Carregamento da imagem
    #Se necessário o redimensioamento da imagem pode vir aqui.
    #Passo 1: Conversão para tons de cinza
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    suave = cv2.GaussianBlur(img, (7, 7), 0) # aplica blur
    (T, bin) = cv2.threshold(suave, 160, 255, cv2.THRESH_BINARY)

    #Passo 4: Detecção de bordas com Canny
    bordas = cv2.Canny(bin, 70, 150)

    objetos, _ = cv2.findContours(bordas.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    imgResultado = frame.copy() # cópia p/ desenhar os resultados finais

    centros = []
    listras_detectadas = 0 

    #definindo parametros de uma fita para que ela seja detectada
    
    continuidade_p = False
     # quadrilatero_p: se o contorno tem 4 vertices, cor_p: se a cor no centro é vermelha, continuidade_p: se a proporção entre os lados é próxima da proporção_predefinida (ex: 2.0 para uma fita de 20cm x 10cm)

    #lista contendo os vertices das possiveis listras detectadas:
    vertices_listras = []
    #print(f"Contornos totais encontrados pelo Canny: {len(objetos)}")

    for contorno in objetos:
        quadrilatero_p = False
        cor_p = False
        proporcao_p = None
        # calcula o perimetro do contorno
        perimetro = cv2.arcLength(contorno, True) # True significa que o contorno é fechado

        # approxPolyDP aproxima a forma geométrica
        # 0.04 (4% do perímetro) é uma tolerância comum para detectar retângulos
        aproximacao = cv2.approxPolyDP(contorno, 0.04 * perimetro, True)
        

        # encontrar o centro usando momentos da imagem 
        #if proporcao_p:
        M = cv2.moments(contorno)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            cor_bgr = frame[cy, cx]
            print(f"Cor original no centro (BGR): {cor_bgr}")
            if cor_bgr[2] > 150 and cor_bgr[0] < 100:
                cor_p = True #Só fazendo os limites de vermelho
            
        # cálculo das distâncias

         
        # se a aprox. tem 4 vertices, significa que temos um quadrilátero (uma lista da fita!!)
        # > 100 é um filtro de área mínima p/ ignorar pequenos ruidos da imagem
        if len(aproximacao) == 4 and cv2.contourArea(contorno) > 100 and cor_p:
            quadrilatero_p = True
            print(f"quadrilatero_p = {quadrilatero_p}")

            #Pegando os tres primeiros vertices para calcular os angulos
            v1 = aproximacao[0][0]
            v2 = aproximacao[1][0]
            v3 = aproximacao[2][0]
            
            d1=math.sqrt((v1[0] - v2[0])**2 + (v2[1] - v1[1])**2)
            d2=math.sqrt((v2[0] - v3[0])**2 + (v3[1] - v2[1])**2) 
             
            proporcao_p=d1/d2
            print(f"Proporção entre os lados: {proporcao_p:.2f}")
            #proporção_predefinida da fita então precisa testar primeiro

            #if proporção=proporção_predefinida:
            #    proporção_p = True
            #listras_detectadas += 1 #colocar como condicao para analisar os centros depois
            cv2.drawContours(imgResultado, [aproximacao], -1, (0, 255, 0), 2)
        
        else:
            print(f"cor_p = {cor_p}")
            print(f"aproximação = {aproximacao}!!!")

        #print(f'\n-> Listra #{listras_detectadas} detectada')
        #print(f'Vértices:\n{aproximacao}')

        if quadrilatero_p and cor_p and proporcao_p:
            centros.append((cx, cy))
            cv2.circle(imgResultado, (cx, cy), 5, (255, 0, 0), -1) 

    # ordenando os centros da esquerda p/ direita p/ garantir que vai medir a distancia entre listras consecutivas
    centros = sorted(centros, key = lambda ponto: ponto[0])
    
    lista_distancias=[]

    for i in range(len(centros) -1):
        '''if proporcao_p == None or cor_p == False or quadrilatero_p == False:
            print(f"-> A listra {i + 1} não atende aos critérios de detecção (quadrilátero: {quadrilatero_p}, cor: {cor_p}, proporção: {proporcao_p})")
            continue'''
        p1 = centros[i]
        p2 = centros[ i + 1]

        # distância euclidiana: d = raiz((x2 - x1)^2 + (y2 - y1)^2)
        distancia = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        lista_distancias.append(distancia)

        cv2.line(imgResultado, p1, p2, (0, 255, 255), 2)

        # calcula o ponto medio
        meio_x = int((p1[0] + p2[0]) / 2)
        meio_y = int((p1[1] + p2[1]) / 2)
        cv2.putText(imgResultado, f"{distancia:.1f}px", (meio_x, meio_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        print(f"Distância entre a listra {i + 1} e a listra {i + 2}: {distancia:.2f} pixels")

    #for i in lista_distancias:
    cv2.imshow('Paredes Virtuais Detectadas', imgResultado)
    
    escreve(img, "Imagem em tons de cinza", 0)
    escreve(suave, "Suavizacao com Blur", 0)
    escreve(bin, "Binarizacao com Metodo Otsu", 255)
    escreve(bordas, "Detector de bordas Canny", 255)

    ultimo_temp = np.vstack([
    np.hstack([img, suave]),
    np.hstack([bin, bordas])
    ])
    ultimo_frame = frame.copy()
    ultimo_objetos = objetos

    if cv2.waitKey(1) & 0XFF == 27: # Esc para sair
            break

imgColorida.release()
cv2.destroyAllWindows()

if ultimo_temp is not None:
    cv2.imshow("Etapas do processamento (Grid)", ultimo_temp)
    cv2.waitKey(0)

    cv2.imshow("Ùltimo frame original", ultimo_frame)
    cv2.drawContours(ultimo_frame, ultimo_objetos, -1, (255, 0, 0), 2)
    cv2.imshow("Todos os contornos encontrados", ultimo_frame)
    cv2.waitKey(0)

cv2.destroyAllWindows()
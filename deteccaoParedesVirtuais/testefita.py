import cv2
import sys
import numpy as np
import math

#Função para facilitar a escrita nas imagem
def escreve(img, texto, cor=(255,255,255)):
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, texto, (10,20), fonte, 0.5, cor, 0, cv2.LINE_AA)

imgColorida = cv2.VideoCapture(2, cv2.CAP_V4L2)
print("Câmera abriu?", imgColorida.isOpened())

if not imgColorida.isOpened():
    print('Não foi possível carregar o vídeo')
    sys.exit()

ultimo_temp = None
ultimo_frame = None
ultimo_objetos = []

while True:
    ok, frame = imgColorida.read()
    if not ok or frame is None:
        print("Não foi possível ler o aquivo de vídeo")
        break
        
    imgResultado = frame.copy() # cópia p/ desenhar os resultados finais
    
    '''#Passo 1: Conversão para tons de cinza
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    '''
    # passo 2: blur para reduzir ruidos
    suave = cv2.GaussianBlur(frame, (7, 7), 0) # aplica blur
    (T, bin) = cv2.threshold(suave, 160, 255, cv2.THRESH_BINARY)

    # passo 3: conversão pra hsv
    hsv = cv2.cvtColor(suave, cv2.COLOR_BGR2HSV)

    red_lower = np.array([0,120,70])
    red_upper = np.array([10,255,255])
    red_mask1 = cv2.inRange(hsv, red_lower, red_upper)

    red_lower2 = np.array([170,120,70])
    red_upper2 = np.array([180,255,255])
    red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)

    # máscara final (só com vermelho)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    #Passo 4: Detecção de bordas com Canny em cima da máscara do vermelho
    bordas = cv2.Canny(red_mask, 70, 150)

    objetos, _ = cv2.findContours(bordas.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centros = []

    listras_detectadas = 0 

    #lista contendo os vertices das possiveis listras detectadas:
    vertices_listras = []
    print(f"Contornos totais encontrados pelo Canny: {len(objetos)}")

    for contorno in objetos:
        # > 100 é um filtro de área mínima p/ ignorar pequenos ruidos da imagem
        if cv2.contourArea(contorno) < 100:
            continue

        perimetro = cv2.arcLength(contorno, True) # True significa que o contorno é fechado
        # 0.04 (4% do perímetro) é uma tolerância comum para detectar retângulos
        aproximacao = cv2.approxPolyDP(contorno, 0.04 * perimetro, True)
         
        # se a aprox. tem 4 vertices, significa que temos um quadrilátero (uma lista da fita!!)
        if len(aproximacao) == 4:
            quadrilatero = True
            print(f"quadrilatero = {quadrilatero}")

            M = cv2.moments(contorno)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

            #Pegando os tres primeiros vertices para conferir a proporção
            v1 = aproximacao[0][0]
            v2 = aproximacao[1][0]
            v3 = aproximacao[2][0]
            
            d1 = math.sqrt((v1[0] - v2[0])**2 + (v2[1] - v1[1])**2)
            d2 = math.sqrt((v2[0] - v3[0])**2 + (v3[1] - v2[1])**2) 

            if d2 != 0:
                proporcao = d1/d2
                # como pode inverter largura/altura, dependendo do angulo da câmera, aceitamos a proporção ou o inversi dela
                # ex: se a fita ideal é 2.0, aceitamos peeto de 2.0 ou perto de 0.5
                if (1.2 <= proporcao <= 2.8) or (0.35 <= proporcao <= 0,8):
                    centros.append((cx, cy))
                    cv2.drawContours(imgResultado, [aproximacao], -1, (0, 255, 0), 2)
                    cv2.circle(imgResultado, (cx, cy), 5, (255, 0, 0), -1)
                    
                    print(f"Proporção entre os lados: {proporcao:.2f}")
                    #proporção_predefinida da fita então precisa testar primeiro

    # ordenando os centros da esquerda p/ direita p/ garantir que vai medir a distancia entre listras consecutivas
    centros = sorted(centros, key = lambda ponto: ponto[0])

    lista_distancias = []

    for i in range(len(centros) - 1):
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

    cv2.imshow('Paredes Virtuais Detectadas', imgResultado)

    # Preparando o Grid de etapas convertendo tudo para 3 canais (BGR)
    img_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_cinza_3c = cv2.cvtColor(img_cinza, cv2.COLOR_GRAY2BGR)
    suave_3c = cv2.cvtColor(cv2.cvtColor(suave, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    mask_3c = cv2.cvtColor(red_mask, cv2.COLOR_GRAY2BGR)
    bordas_3c = cv2.cvtColor(bordas, cv2.COLOR_GRAY2BGR)
    
    escreve(img_cinza_3c, "Imagem em tons de cinza", 0)
    escreve(suave_3c, "Suavizacao com Blur", 0)
    escreve(mask_3c, "Filtro de cor vermelha (HSV)", 255)
    escreve(bordas_3c, "Detector de bordas Canny", 255)

    ultimo_temp = np.vstack([
    np.hstack([img_cinza_3c, suave_3c]),
    np.hstack([mask_3c, bordas_3c])
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
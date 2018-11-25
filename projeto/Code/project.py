import numpy as np
import scipy
import scipy.ndimage as scp
import cv2
from skimage import feature, filters, morphology
from skimage.transform import hough_line, hough_line_peaks, probabilistic_hough_line
import utils


def projeto_sobel(imagem):
    
    imagem = 1 - (np.max(imagem)-imagem)/(np.max(imagem)-np.min(imagem))

    img = filters.rank.minimum(imagem, morphology.square(7)) 

    imagem = scp.morphology.grey_opening(img,size=7) 
    imagem = scp.morphology.grey_closing(imagem,size=5)

    borda = feature.canny(imagem,sigma=1) 

    borda = scp.morphology.binary_closing(borda) 

    return borda,imagem

def projeto_canny(imagem):

    img = scp.morphology.grey_closing(imagem,size=17) 
    img = scp.morphology.grey_opening(img,size=17)

    imagem = imagem - img 

    img = 1 - (np.max(imagem)-imagem)/(np.max(imagem)-np.min(imagem))

    borda = feature.canny(img,sigma=1) 

    return borda, imagem

def canny_por_canal(imagem):
    red = imagem[:,:,0]
    green = imagem[:,:,1] 
    blue = imagem[:,:,2]

    canny_r = feature.canny(red,sigma=1)
    canny_r = scp.morphology.binary_closing(canny_r,structure=np.ones((3,3)))
    canny_r = scp.morphology.binary_opening(canny_r, structure=np.ones((3,3)))

    canny_g = feature.canny(green,sigma=1)
    canny_g = scp.morphology.binary_closing(canny_g,structure=np.ones((3,3)))
    canny_g = scp.morphology.binary_opening(canny_g,structure=np.ones((3,3)))

    canny_b = feature.canny(blue,sigma=1)
    canny_b = scp.morphology.binary_closing(canny_b,structure=np.ones((3,3)))
    canny_b = scp.morphology.binary_opening(canny_b,structure=np.ones((3,3)))

    a,b,c = np.shape(imagem)
    result = np.zeros((a,b))

    for x in range(np.shape(imagem)[0]):
        for y in range(np.shape(imagem)[1]):
            if canny_r[x][y] and canny_b[x][y]:
                result[x][y] = 1
            elif canny_r[x][y] and canny_g[x][y]:
                result[x][y] = 1
            elif canny_b[x][y] and canny_g[x][y]:
                result[x][y] = 1
            else:
                result[x][y] = 0

    return result

def projeto_rodrigo(imagem):
    borda = feature.canny(imagem,sigma=1)

    block_size = 45
    img = filters.threshold_adaptive(imagem,block_size,offset=10)
    img = 1 - img
    img = morphology.skeletonize(img)

    res = borda + img

    for x in range(np.shape(res)[0]):
        for y in range(np.shape(res)[1]):
            if res[x][y] > 0:
                res[x][y] = 1

    res = scp.morphology.grey_closing(res,size=9)

    return borda, img, res

def detecta_rejunte(imagem):
    # gray = cv2.cvtColor
    # (imagem,cv2.COLOR_BGR2GRAY)
    # ret, thresh = cv2.threshold(gray,0,255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    # return ret, thresh
    imgf = scp.gaussian_filter(imagem,1.0)
    labeled, nr_objects = scp.label(imgf > (np.min(imagem)+np.max(imagem))/2)
    labeled = labeled > np.min(labeled)
    labeled = morphology.erosion(scp.morphology.binary_erosion(morphology.erosion(labeled)))
    # print(nr_objects)
    return labeled

# funciona pra 19
def projeto_aryell(imagem):
    aux = np.shape(imagem)
    retorno = np.zeros(aux)
    
    naoRejunte = detecta_rejunte(imagem)
    bordaDilatada = projeto_canny(imagem)
    for a in range(aux[0]-1):
        for b in range(aux[1]-1):
            retorno[a][b] = bordaDilatada[a][b] and naoRejunte[a][b]
    retorno = scp.morphology.binary_erosion(retorno)
    return retorno 

def projeto_aryell_2(imagem):
    aux = np.shape(imagem[:][:][0])
    retorno = np.zeros(aux)
    borda = canny_por_canal(imagem)
    rejunte = utils.extraiRetas(borda,130)
    # esqueleto = morphology.skeletonize(imagem)
    # rejunte = utils.extraiRetas(esqueleto,130)
    # print(rejunte)
    for a in range(aux[0]-1):
        for b in range(aux[1]-1):
            retorno[a][b] = borda[a][b] and (not rejunte[a][b])
    return retorno, borda, rejunte, imagem

# funciona mais ou menos para alguns
def projeto_aryell_3(imagem):
    aux = np.shape(imagem)
    retorno = np.zeros(aux)
    # extrai borda
    # borda,_ = projeto_canny(imagem)
    print('aaaa')
    # extrai retas com threshold maior que 130
    retas = utils.extraiRetas(imagem,400)
    # cria imagem de retorno apartir do esqueleto e das retas
    for a in range(aux[0]-1):
        for b in range(aux[1]-1):
            retorno[a][b] = imagem[a][b] and (not retas[a][b])
    
    return retorno, imagem, retas, imagem
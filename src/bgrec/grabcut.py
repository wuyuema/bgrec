import cv2 as cv
import numpy as np

# 640 为魔法参数
# 初始化图片所用的倍率缩放参数
magic1 = 640
# 高斯模糊参数
magic2 = 5
# grabcut 计算次数
magic3 = 5

class grab_cut:
    global magic1, magic2, magic3

    # 参数初始化
    def __init__(self, img):
        self.__img = img
        self.__raw = self.__img.copy()
        self.__height = img.shape[0]
        self.__width = img.shape[1]

        self.__scale = magic1 * self.__width // self.__height
        if self.__width > magic1:
            self.__img = cv.resize(self.__img, (magic1, self.__scale), interpolation=cv.INTER_AREA)
        
        self.__show = self.__img.copy()
        self.__gc = self.__img.copy()
        self.__gc = cv.GaussianBlur(self.__gc, (magic2, magic2), 0)

        self.__mask = np.zeros((self.__height, self.__width), np.uint8)
        self.__mask[:, :] = 2

    def __get_fg(self):
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        rect = (1, 1, self.__height, self.__width)

        cv.grabCut(self.__gc, self.__mask, rect, bgdModel, fgdModel, magic3, cv.GC_INIT_WITH_MASK)
        mask2 = np.where((self.__mask == 2) | (self.__mask == 0), 0, 1).astype('uint8')
        sho = mask2.copy()
        _, sho = cv.threshold(sho, 0, 255, cv.THRESH_BINARY)
        sho2 = mask2.copy()
        _, sho2 = cv.threshold(sho, 0, 1, cv.THRESH_BINARY_INV)
        # cv.imshow('mask2', sho)
        # cv.imshow('mask3', sho2)
        return self.__gc, sho2

    def __expand_mask(self, xor_dil):
        ex_scale = self.__height // xor_dil.shape[0]
        for i in range(xor_dil.shape[0]):
            for j in range(xor_dil.shape[1]):
                if (xor_dil[i, j] > 0): 
                    cv.rectangle(self.__mask, (i * ex_scale, j * ex_scale), ((i + 1) * ex_scale - 1, (j + 1) * ex_scale - 1), 1, -1, 4)

    def on_mask_produce(self, param):
        # self.__mask = param[:, :, 0]
        self.__expand_mask(param)
        # _, showing = cv.threshold(self.__mask, 0, 255, cv.THRESH_BINARY)
        # cv.imshow('fgmask', showing)
        return self.__get_fg()

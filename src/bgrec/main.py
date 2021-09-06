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

        self.__mask = np.zeros((self.__width, self.__height), np.uint8)
        self.__mask[:, :] = 2

    def __get_fg(self):
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        rect = (1, 1, self.__height, self.__width)

        cv.grabCut(self.__gc, self.__mask, rect, bgdModel, fgdModel, magic3, cv.GC_INIT_WITH_MASK)
        return self.__gc

    def on_mask_produce(self, param):
        self.__mask = param[:, :, 0]
        for i in range(len(self.__mask[:])):
            for j in range(len(self.__mask)):
                self.__mask[i, j] = 1 if self.__mask[i, j] > 0 else 0
        return self.__get_fg()

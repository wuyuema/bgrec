import cv2 as cv
import numpy as np

# 高斯模糊参数
magic1 = 5


class canny:
    def __init__(self, img, param):
        self.__img = img
        self.__raw = self.__img.copy()
        self.__height = self.__img.shape[0]
        self.__width = self.__img.shape[1]
        self.__param = param

        self.__blur = self.__raw.copy()
        self.__blur = cv.cvtColor(self.__blur,
                                  cv.COLOR_BGR2GRAY)
        self.__blur = cv.GaussianBlur(self.__blur, (magic1, magic1), 0)

        self.__canny = self.__raw.copy()

    def get_canny(self):
        self.__canny = cv.Canny(self.__canny, self.__param, self.__param * 3)
        return self.__canny


class canny_clps:
    def __init__(self, img, canny_scale, collapse_scale):
        self.__img = img
        self.__raw = self.__img.copy()
        self.__height = self.__img.shape[0]
        self.__width = self.__img.shape[1]
        self.__param = collapse_scale

        self.__canny = canny(self.__img, canny_scale)
        self.__outline = self.__canny.get_canny()

        self.__clps = np.zeros((self.__height, self.__width),
                               np.uint8)

    def get_clps(self):
        self.__clps = self.__outline.copy()

        self.__clps = cv.blur(self.__clps, (self.__param, self.__param))
        _, self.__clps = cv.threshold(self.__clps, 127, 255,
                                      cv.THRESH_BINARY)

        kernel = cv.getStructuringElement(cv.MORPH_RECT,
                                          (self.__param * 3, self.__param * 3))
        self.__clps = cv.dilate(self.__clps, kernel)
        _, self.__clps = cv.threshold(self.__clps, 0, 255,
                                      cv.THRESH_BINARY)

        return self.__clps

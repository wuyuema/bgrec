import numpy as np
import cv2 as cv
import time




def shrink(src, pixnum):
    res = np.zeros((int(src.shape[0] / pixnum),
                   int(src.shape[1] / pixnum)), np.uint8)
    for i in range(res.shape[0]):
        for j in range(res.shape[1]):
            areatot = 0
            for ii in range(i * pixnum, (i + 1) * pixnum):
                for ij in range(j * pixnum, (j + 1) * pixnum):
                    if src[ii, ij] > 0:
                        areatot = 1
                        break
                if areatot > 0:
                    break
            if areatot > 0:
                res[i, j] = 255
    return res

if __name__ == '__main__':
    cap = cv.VideoCapture(1)
    fps = cap.get(cv.CAP_PROP_FPS)
    tpf = int(1000 / fps)
    height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
    _, img = cap.read()
    init_blur = cv.GaussianBlur(img, (5, 5), 0)
    can = cv.Canny(init_blur, 50, 150)
    canner = can
    shrinkpix = 4
    ticks = time.time()
    choock = ticks
    dtime = 0
    dil = np.zeros(can.shape, np.uint8)

    tmp = shrink(canner, shrinkpix)
    last_canner = tmp
    pure = np.zeros(can.shape, np.uint8)

    picount = np.zeros(img.shape[:-1], np.uint8)
    result = np.zeros(img.shape, np.uint8)

    while (cap.isOpened()):
        if (cv.waitKey(tpf) & 0xFF == ord('q')):
            break
        _, frame = cap.read()

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        hitem = hsv.copy()
        hitem[:, :, 1] = 255
        hitem[:, :, 2] = 255
        # pure = cv.cvtColor(hitem, cv.COLOR_HSV2BGR)
        singleH = hsv[:, :, 0]

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        bin = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)

        blur = cv.GaussianBlur(gray, (5, 5), 0)
        # cv.imshow('blur', blur)
        # blur = cv.GaussianBlur(singleH, (5, 5), 0)
        canny = cv.Canny(blur, 60, 180)
        # canny = cv.Canny(pure, 230, 255)
        ticks = time.time()
        dtime = ticks - choock
        # tmp = canner

        if dtime > 2:
            choock = ticks
            canner = can
            can = canny
            shrinked = shrink(canner, shrinkpix)
            # tmp = cv.bitwise_xor(canner, last_canner)
            tmp = cv.bitwise_xor(shrinked, last_canner)

            # 中值模糊接阈值
            tmp = cv.medianBlur(tmp, 5)
            # tmp = cv.threshold(tmp, 127, 255, cv.THRESH_BINARY)

            # 膨胀扩散
            dil = np.zeros(canny.shape, np.uint8)
            for i in range(tmp.shape[0]):
                for j in range(tmp.shape[1]):
                    for ii in range(i * shrinkpix, (i + 1) * shrinkpix):
                        for ij in range(j * shrinkpix, (j + 1) * shrinkpix):
                            dil[ii, ij] = tmp[i, j]

            # 获取轮廓
            cont, _ = cv.findContours(
                dil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_TC89_L1)
            # 获取外点
            outerPoints = list()
            for i in range(tmp.shape[0]):
                for j in range(tmp.shape[1]):
                    if tmp[i, j] != 0:
                        outerPoints.append([j, i])

            if len(outerPoints) == 0:
                pass
            else:
                for i in range(len(outerPoints), 3):
                    outerPoints.append(outerPoints[0])
                aryPoints = np.array(outerPoints)

            # 获取凸包
            hull = cv.convexHull(aryPoints)
            # print(type(cont[0]))

            # 绘制凸包
            hullimg = frame.copy()
            for w in hull:
                w *= 5
            cv.polylines(hullimg, [hull], True, (255, 0, 0), 2)
            cv.imshow('dil', dil)
            cv.imshow('hullimg', hullimg)

            # 根据凸包创建蒙版
            mask = np.zeros(frame.shape, np.uint8)
            cv.fillPoly(mask, [hull], (255, 255, 255))
            cv.imshow('mask', mask)

            # 图像的选择性叠加
            # 白色统计
            for i in range(mask.shape[0]):
                for j in range(mask.shape[1]):
                    if mask[i, j, 0] == 0:
                        picount[i, j] += 1

                        # BGR 加权叠加
                        for k in range(3):
                            result[i, j, k] = (result[i, j, k] * (picount[i, j] - 1) + frame[i, j, k]) / picount[i, j]
            
            cv.imshow('result', result)

            last_canner = shrinked
        else:
            can += canny
        # hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        cv.imshow('raw', frame)
        
        # cv.imshow('hsv', hsv)
        # cv.imshow("pure", hsv[:, :, 0])
        # cv.imshow('superpure', pure)
        cv.imshow('canny', canny)
        # cv.imshow('shrink', dil)
    cap.release()
    cv.destroyAllWindows()

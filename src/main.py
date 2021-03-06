import cv2 as cv
import numpy as np
import sys
import time
import os

import bgrec
import listcam


# 辅助函数: 获得按键以 char 形式返回
def getcvinput(delaytime):
    raw = cv.waitKey(delaytime) & 0xFF
    return chr(raw)


# 每帧更新时回调
def on_frame_upd(cap):
    # 读取帧
    _, frame = cap.read()

    # 显示原始帧
    # cv.imshow('raw', frame)

    dil = bgrec.clps(frame, 50, 3).get_clps()
    # cv.imshow('dil', dil)
    return dil


def on_spec_upd(last_tot, tot_dil, res, cap, cntmask):
    # xor_dil = cv.bitwise_and(last_tot, np.zeros((height, width), np.uint8), mask=tot_dil)
    # xor2 = cv.bitwise_and(tot_dil, np.zeros((height, width), np.uint8), mask=last_tot)
    # xor_dil = cv.bitwise_or(xor2, xor_dil)
    shrink1 = bgrec.shrk(last_tot, 5)
    shrink2 = bgrec.shrk(tot_dil, 5)
    # shrink1 = last_tot
    # shrink2 = tot_dil
    shrink1 = cv.medianBlur(shrink1, 5)
    shrink2 = cv.medianBlur(shrink2, 5)
    _, shrink1 = cv.threshold(shrink1, 127, 255,
                              cv.THRESH_BINARY)
    _, shrink2 = cv.threshold(shrink2, 127, 255,
                              cv.THRESH_BINARY)
    xor_dil = cv.bitwise_xor(shrink1, shrink2)
    xor_dil = cv.medianBlur(xor_dil, 5)
    _, xor_dil = cv.threshold(xor_dil, 127, 255,
                              cv.THRESH_BINARY)

    _, img = cap.read()
    grabcut = bgrec.gc(img)
    gc, mask = grabcut.on_mask_produce(xor_dil)
    mask2 = mask.copy()
    ans = gc * mask2[:, :, np.newaxis]

    # cv.imshow('ans', ans)
    last_cntmask = cntmask.copy()
    cntmask = cntmask + mask
    for i in range(res.shape[0]):
        for j in range(res.shape[1]):
            for k in range(res.shape[2]):
                if (cntmask[i, j] == 0):
                    continue
                res[i, j, k] = (
                    res[i, j, k] * last_cntmask[i, j] + ans[i, j, k]) // cntmask[i, j]

    # res = (res * last_cntmask + ans) / cntmask

    return tot_dil.copy(), xor_dil, res, cntmask


if __name__ == '__main__':

    # 获取相机列表
    cams = listcam.prt_cam()

    # 用户交互选择相机
    def get_cam_num(cams):
        # 用户交互选择相机
        while True:
            cam = input(
                'Please input the video file path, or the camera id (available cameras: {}): '.format(cams[:-1]))
            try:
                if (int(cam) == eval(cam) and int(cam) < len(cams)):
                    cam = int(cam)
                    break
                else:
                    while True:
                        buf = input(
                            'Illegal input. Need to input again? (y/n): ')
                        if (buf == 'y' or buf == 'Y'):
                            break
                        elif (buf == 'n' or buf == 'N'):
                            sys.exit()
                        else:
                            continue
            except:
                if not (os.path.isfile(cam)):
                    while True:
                        buf = input('Illegal input. Need to input again? (y/n): ')
                        if (buf == 'y' or buf == 'Y'):
                            break
                        elif (buf == 'n' or buf == 'N'):
                            sys.exit()
                        else:
                            continue

        return cam

    cam = get_cam_num(cams)

    # cv 捕获相机
    cap = cv.VideoCapture(cam)

    # cv 获得相机参数
    fps = cap.get(cv.CAP_PROP_FPS)
    height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
    height = int(height)
    width = int(width)
    # tpf = 1000 / fps
    # Time Per Frame
    tpf = round(1000 / fps, 0)
    tpf = int(tpf)

    dark_canvas = np.zeros((height, width), np.uint8)
    last_tot = dark_canvas.copy()
    tot_dil = dark_canvas.copy()

    # 特殊操作时点
    buf = input('Please give a execute time, if you don\'t know what to do, press enter: ')
    if (buf == ''):
        d_time = 3
    else:
        d_time = eval(buf)
    s_time = time.time()

    # 最终答案格式
    cntmask = np.zeros((height, width), np.uint64)
    res = np.zeros((height, width, 3), np.uint8)
    cnt = 0

    # 函数主循环
    while (cap.isOpened()):
        # 按下q退出
        buf = getcvinput(tpf)
        if (buf == 'q'):
            break
        elif (buf == 's'):
            cnt += 1
            cv.imwrite('../res/{}.jpg'.format(cnt), res)

        # 执行每帧更新
        tot_dil += on_frame_upd(cap)

        _, tot_dil = cv.threshold(tot_dil, 0, 255, cv.THRESH_BINARY)

        # 每隔一定时间更新
        tick = time.time()

        if (tick - s_time > d_time):
            s_time = tick
            last_tot, xor, res, cntmask = on_spec_upd(
                last_tot.copy(), tot_dil.copy(), res, cap, cntmask)
            # cv.imshow('tot', last_tot)
            tot_dil[:, :] = 0
            # cv.imshow('xor', xor)
            cv.imshow('res', res)

    cap.release()
    cv.destroyAllWindows()

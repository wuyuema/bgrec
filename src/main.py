import cv2 as cv
import numpy as np
import sys
import time

import bgrec
import listcam


# 辅助函数: 获得按键以 char 形式返回
def getcvinput(delaytime):
    raw = cv.waitKey(tpf) & 0xFF
    return chr(raw)


# 每帧更新时回调
def on_frame_upd():
    # 读取帧
    _, frame = cap.read()

    # 显示原始帧
    cv.imshow('raw', frame)


if __name__ == '__main__':

    # 获取相机列表
    cams = listcam.prt_cam()

    # 用户交互选择相机
    def get_cam_num(cams):
        # 用户交互选择相机
        while True:
            cam = input(
                'Please input the camera id (available cameras: {}): '.format(cams[:-1]))
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
    # tpf = 1000 / fps
    # Time Per Frame
    tpf = round(1000 / fps, 0)
    tpf = int(tpf)

    # 函数主循环
    while (cap.isOpened()):
        # 按下q退出
        if (getcvinput(tpf) == 'q'):
            break

        # 执行每帧更新
        on_frame_upd()

    cap.release()
    cv.destroyAllWindows()

import cv2 as cv

def prt_cam():
    cams = []
    i = 0
    while True:
        cap = cv.VideoCapture(i, cv.CAP_DSHOW)
        if (not cap.isOpened()):
            break
        cams.append(i)
        cap.release()
        i += 1
    return cams

# print(prt_cam())
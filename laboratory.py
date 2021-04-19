import cv2
import numpy as np

from display import show


# path = 'opencv_tests/lab-latest-1.jpg'
# frame = cv2.imread(path)
# if frame is None:
#     exit(f'Could not read the image.\n{path}')


def scan():
    cap = cv2.VideoCapture(0)
    cap.set(3, 960)
    cap.set(4, 540)
    flag, frame = cap.read()
    rects = []
    result = []
    # hsv1_colors = (50, 180, 0)
    hsv1_colors = (60, 70, 20)
    # hsv2_colors = (180, 255, 200)
    hsv2_colors = (89, 145, 255)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    zeros = np.zeros(hsv.shape)

    h_min = np.array(hsv1_colors, np.uint8)
    h_max = np.array(hsv2_colors, np.uint8)

    mask = cv2.inRange(hsv, h_min, h_max)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_rects = 0, 0, 0, 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w * h > max_rects[2] * max_rects[3]:
            max_rects = x, y, w, h
        if w > 5 and h > 10:
            rects.append((w, h, x))
            cv2.putText(zeros, text=f'({w}, {h})', org=(x, y),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0),
                        thickness=1, lineType=cv2.LINE_AA)
            cv2.rectangle(zeros, (x, y), (x + w, y + h), (155, 155, 0), 1)
    rects.sort(key=lambda _: _[2])
    for num, (w, h, x) in enumerate(rects):
        # print(num, (w, h))
        # print(w)
        # print(h)
        if 15 < w < 70:
            if h > 300:
                typ = 3
            elif h > 150:
                typ = 2
            elif h > 70:
                typ = 1
            else:
                typ = -1
            if typ > 0:
                result.append(str(typ))
        if len(result) > 5:
            pass
    print(' '.join(result))
    show(' '.join(result))


if __name__ == '__main__':
    scan()

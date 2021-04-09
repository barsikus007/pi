import os
import subprocess

# subprocess.Popen('source ~/.bashrc'.split()).wait()
# python3 ~/Desktop/pycharm/laboratory.py

import cv2
import numpy as np


def scan():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        rects = []
        result = []
        hsv_colors = [50, 180, 0]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        zeros = np.zeros(hsv.shape)

        h_min = np.array(hsv_colors, np.uint8)
        h_max = np.array([180, 255, 200], np.uint8)

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
        img = zeros
        # img = cv2.drawContours(zeros, contours, -1, (0, 255, 0), 3)
        rects.sort(key=lambda _: _[2])
        for num, (w, h, x) in enumerate(rects):
            # print(num, (w, h))
            # print(w)
            # print(h)
            if h > 300:
                typ = 3
            elif h > 200:
                typ = 2
            elif h > 100:
                typ = 1
            else:
                typ = -1
            if typ > 0:
                result.append(str(typ))
        cv2.imshow('cum', frame)
        cv2.imshow('result', img)
        print(' '.join(result))

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
        if cv2.waitKey(5) & 0xFF == ord('й'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    scan()

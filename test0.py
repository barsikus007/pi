import numpy as np
import cv2
import time


def main_video():
    fps = 0
    show_fps = 0
    temp_time = int(time.time())
    cap = cv2.VideoCapture(0)
    while True:

        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        fps += 1
        if temp_time != int(time.time()):
            print(fps)
            show_fps = fps
            fps = 0
        temp_time = int(time.time())
        font = cv2.FONT_HERSHEY_PLAIN
        frame = cv2.putText(frame, f'FPS {show_fps}', (0, 15), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        frame = cv2.putText(frame, f'FPS {show_fps}', (0, 30), font, 1, (0, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow('test', frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        b, g, r = cv2.split(frame)

        sift = cv2.SIFT_create()
        kp = sift.detect(gray, None)
        siftt = cv2.drawKeypoints(gray, kp, frame)

        ret, threshold_image = cv2.threshold(frame, 127, 255, 0)

        cv2.imshow('green', g)
        cv2.imshow('gray', gray)
        cv2.imshow('threshold_image', threshold_image)
        cv2.imshow('sift', siftt)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.waitKey(1) & 0xFF == ord('й'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def main_photo(path):
    frame = cv2.imread(path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    b, g, r = cv2.split(frame)

    ret, threshold_image = cv2.threshold(frame, 127, 255, 0)

    sift = cv2.SIFT_create()
    kp = sift.detect(gray, None)
    siftt = cv2.drawKeypoints(frame, kp, frame)

    cv2.imshow('green', g)
    cv2.imshow('gray', gray)
    cv2.imshow('threshold_image', threshold_image)
    cv2.imshow('sift', siftt)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main_video()
    # main_photo('lab.png')

import numpy as np
import cv2
import time


def main_video():
    fps = 0
    show_fps = 0
    temp_time = int(time.time())
    cap = cv2.VideoCapture(0)
    cap.set(3, 960)
    cap.set(4, 540)
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
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.waitKey(1) & 0xFF == ord('й'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main_video()
    # main_photo('lab-latest-1.jpg')
"""sudo apt install libgtk-3-dev libcanberra-gtk3-dev -y
sudo apt install libtiff-dev zlib1g-dev -y
sudo apt install libjpeg-dev libpng-dev -y
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt-get install libxvidcore-dev libx264-dev -y"""
import cv2
import numpy as np


photo_mode = False
print(cv2.getBuildInformation())


def gradientHSV(h_min, h_max, w=200):
    colors = np.zeros((1, w, 3), np.uint8)

    step = (h_max - h_min) / w
    step = step.reshape((1, 1, 3))

    color_hsv = h_min + step
    colors[:, 0] = color_hsv
    for i in range(1, w):
        color_hsv += step
        colors[:, i] = color_hsv

    return colors


if __name__ == '__main__':
    cv2.namedWindow("result")  # создаем главное окно
    cv2.namedWindow("settings", cv2.WINDOW_NORMAL)  # создаем окно настроек
    cv2.resizeWindow("settings", 500, 500)

    if not photo_mode:
        cap = cv2.VideoCapture(0)
        cap.set(3, 960)
        cap.set(4, 540)

    # создаем 6 бегунков для настройки начального и конечного цвета фильтра
    cv2.createTrackbar('h1', 'settings', 60, 179, lambda x: None)
    cv2.createTrackbar('s1', 'settings', 70, 255, lambda x: None)
    cv2.createTrackbar('v1', 'settings', 20, 255, lambda x: None)
    cv2.createTrackbar('h2', 'settings', 89, 179, lambda x: None)
    # cv2.createTrackbar('h2', 'settings', 179, 179, lambda x: None)
    cv2.createTrackbar('s2', 'settings', 145, 255, lambda x: None)
    # cv2.createTrackbar('s2', 'settings', 255, 255, lambda x: None)
    cv2.createTrackbar('v2', 'settings', 255, 255, lambda x: None)
    # cv2.createTrackbar('v2', 'settings', 255, 255, lambda x: None)
    # P.S: чтобы поместить диапазон значений Hue (от 0 до 360) в рамки целевого формата (8 бит),
    #      OpenCV делит данный диапазон на 2. Следовательно Hue в OpenCV работает в диапазоне 0 до 179

    while True:
        if photo_mode:
            img = cv2.imread('lab-latest-2.jpg')
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            # frame = cv2.imread('lab.png')
        else:
            flag, img = cap.read()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # считываем значения бегунков
        h1 = cv2.getTrackbarPos('h1', 'settings')
        s1 = cv2.getTrackbarPos('s1', 'settings')
        v1 = cv2.getTrackbarPos('v1', 'settings')
        h2 = cv2.getTrackbarPos('h2', 'settings')
        s2 = cv2.getTrackbarPos('s2', 'settings')
        v2 = cv2.getTrackbarPos('v2', 'settings')

        # формируем начальный и конечный цвет фильтра
        h_min = np.array((h1, s1, v1), np.uint8)
        h_max = np.array((h2, s2, v2), np.uint8)

        # накладываем фильтр на кадр в модели HSV
        thresh = cv2.inRange(hsv, h_min, h_max)

        # добавляем визуализацию цветового диапазона
        gradient = gradientHSV(h_min, h_max)
        gradient = cv2.cvtColor(gradient, cv2.COLOR_HSV2BGR)

        # выводим результат на экран
        cv2.imshow('frame', img)
        cv2.imshow('result', thresh)
        cv2.imshow('settings', gradient)

        ch = cv2.waitKey(5)
        if ch == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

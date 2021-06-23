import cv2
import mediapipe as mp
import time, autopy
import numpy as np
import math
import pyautogui as pt
from pynput.mouse import Button, Controller as MouseController
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
print(volRange)
Mouse = MouseController()


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.holistic
mode = ''


tipIds = [4, 8, 12, 16, 20]
active = 0

cap = cv2.VideoCapture(0)

with mp_hands.Holistic(min_detection_confidence=0.5,min_tracking_confidence=0.5) as hands:
     while cap.isOpened():
         while True:
             lmList = []
             fingers = []

             success, image = cap.read()
             start = time.time()

             image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

             image.flags.writeable = False

             results = hands.process(image)

             image.flags.writeable = True

             image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

             if results.right_hand_landmarks:
                 myHand = results.right_hand_landmarks
                 mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_hands.HAND_CONNECTIONS)
                 for id, lm in enumerate(myHand.landmark):
                     h, w, c = image.shape
                     cx, cy = int(lm.x * w), int(lm.y * h)
                     lmList.append([id, cx, cy])

#######################################################   ----------------- Controller -----------------   ###################################################################################
             if len(fingers) == 0:
                 if len(lmList) != 0:
                     #Thumb
                     if lmList[tipIds[0]][1] > lmList[tipIds[0 -1]][1]:
                         if lmList[tipIds[0]][1] >= lmList[tipIds[0] - 1][1]:
                             fingers.append(1)
                         else:
                             fingers.append(0)
                     elif lmList[tipIds[0]][1] < lmList[tipIds[0 -1]][1]:
                         if lmList[tipIds[0]][1] <= lmList[tipIds[0] - 1][1]:
                              fingers.append(1)
                         else:
                             fingers.append(0)

                     for id in range(1,5):
                         if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                             fingers.append(1)
                         else:
                             fingers.append(0)



                     if (fingers == [0,0,0,0,0]) & (active == 0):
                         mode='Free'
                     elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (active == 0):
                         mode = 'Scroll'
                         #active = 1
                     elif (fingers == [1, 1, 0, 0, 0]) & (active == 0):
                          mode = 'Volume'
                         # active = 1
                     elif (fingers == [1, 1 , 1, 1, 1] or fingers == [0, 1, 1, 1, 1]) & (active == 0):
                          mode = 'Cursor'
                         # active = 1



########################################################################----------  Scroll  ---------##########################################################################################

                     if mode == 'Scroll':
                          active == 1
                          if len(lmList) != 0:
                              if fingers == [0,1,0,0,0]:
                                  mode = 'Scroll (Up)'
                                  pt.scroll(100)
                              if fingers == [0,1,1,0,0]:
                                  mode = 'Scroll (Down)'
                                  pt.scroll(-100)
                              if fingers == [0,0,0,0,0]:
                                  mode = 'Free'
                                  active == 0
##################################################################---------   Cursor   ----------#############################################################################################


                     if mode == 'Cursor':
                         active == 1
                         if len(lmList) != 0:
                             if fingers[1:] == [1,1,1,1]:
                                 x1, y1 = lmList[8][1], lmList[8][2]
                                 w, h = autopy.screen.size()
                                 X = int(np.interp(x1, [110, 620], [0, w - 1]))
                                 Y = int(np.interp(y1, [20, 350], [0, h - 1]))
                                 cv2.circle(image, (lmList[8][1], lmList[8][2]), 5, (0, 255, 0), cv2.FILLED)
                                 cv2.circle(image, (lmList[4][1], lmList[4][2]), 5, (0, 255, 255), cv2.FILLED)
                                 #X/2,Y/2
                                 #print(X,Y)
                                 Mouse.position = (X,Y)
                             if fingers == [0,1,1,1,1]:
                                 Mouse.press(Button.left)
                             #elif fingers == [1, 1, 1, 1, 1]:
                                 Mouse.release(Button.left)


####################################################################   -----   VOLUME   -----#################################################################################################
                     if mode == 'Volume':
                         active == 1
                         if len(lmList) != 0:
                             distance_volume = round((math.sqrt(math.pow(lmList[4][1] - lmList[8][1], 2) + math.pow(lmList[4][2] - lmList[8][2] ,2))/5))
                             volume.SetMasterVolumeLevel(-distance_volume, None)
                             #print(distance_volume)


###########################################################################################################################################################################################

             end = time.time()
             totalTime = end - start

             fps = 1 / totalTime
             if mode == 'Volume':
                 try:
                     cv2.putText(image, f'Volume: {int(distance_volume)}', (10,340), cv2.FONT_HERSHEY_SIMPLEX, 1, (50,50,50), 2)
                 except:
                     continue
             cv2.putText(image, f'FPS: {int(fps)}', (10,460), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
             cv2.putText(image, f'Mode: {str(mode)}', (10,400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

             cv2.imshow('hand', image)


             if cv2.waitKey(5) & 0xFF == 27:
                 print(results.right_hand_landmarks[0])
                 break

     cap.release()

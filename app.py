from streamlit_webrtc import webrtc_streamer
import av
import cv2
import os
from keras.models import load_model
import numpy as np
from pygame import mixer
from playsound import playsound

#mixer.music.load('alarm.wav')
#sound = mixer.Sound('alarm.wav')
fc=os.path.dirname(cv2.__file__)+"/data/haarcascade_frontalface_alt.xml"
lc=os.path.dirname(cv2.__file__)+"/data/haarcascade_lefteye_2splits.xml"
rc=os.path.dirname(cv2.__file__)+"/data/haarcascade_righteye_2splits.xml"
face = cv2.CascadeClassifier(fc)
leye = cv2.CascadeClassifier(lc)
reye = cv2.CascadeClassifier(rc)
lbl = ['Close', 'Open']
model = load_model('models/cnnCat2.h5')
path = os.getcwd()
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
count = 0
score = 0
thicc = 2

def callback(frame:av.VideoFrame)->av.VideoFrame:
    global count
    global score
    global thicc
    global label
    rpred = [99]
    lpred = [99]
    frame=frame.to_ndarray(format="bgr24")
    height, width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face.detectMultiScale(gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))
    left_eye = leye.detectMultiScale(gray)
    right_eye = reye.detectMultiScale(gray)

    cv2.rectangle(frame, (0, height - 50), (200, height), (0, 0, 0), thickness=cv2.FILLED)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 1)

    for (x, y, w, h) in right_eye:
        r_eye = frame[y:y + h, x:x + w]
        count = count + 1
        r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
        r_eye = cv2.resize(r_eye, (24, 24))
        r_eye = r_eye / 255
        r_eye = r_eye.reshape(24, 24, -1)
        r_eye = np.expand_dims(r_eye, axis=0)
        predict_r = model.predict(r_eye)
        rpred = np.argmax(predict_r, axis=1)
        # rpred = model.predict_classes(r_eye)
        if (rpred[0] == 1):
            lbl = 'Open'
        if (rpred[0] == 0):
            lbl = 'Closed'
        break

    for (x, y, w, h) in left_eye:
        l_eye = frame[y:y + h, x:x + w]
        count = count + 1
        l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
        l_eye = cv2.resize(l_eye, (24, 24))
        l_eye = l_eye / 255
        l_eye = l_eye.reshape(24, 24, -1)
        l_eye = np.expand_dims(l_eye, axis=0)
        predict_l = model.predict(l_eye)
        lpred = np.argmax(predict_l, axis=1)
        # lpred = model.predict_classes(l_eye)
        if (lpred[0] == 1):
            lbl = 'Open'
        if (lpred[0] == 0):
            lbl = 'Closed'
        break

    if (rpred[0] == 0 and lpred[0] == 0):
        score = score + 1
        cv2.putText(frame, "Closed", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
    # if(rpred[0]==1 or lpred[0]==1):
    else:
        score = score - 1
        cv2.putText(frame, "Open", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

    if (score < 0):
        score = 0
    cv2.putText(frame, 'Score:' + str(score), (100, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
    if (score >=10):
        # person is feeling sleepy so we beep the alarm
        try:
            playsound('alarm.wav')
            #pygame.mixer.music.play(0)

        except:  # isplaying = False
            pass
        if (thicc < 16):
            thicc = thicc + 2
        else:
            thicc = thicc - 2
            if (thicc < 2):
                thicc = 2
        cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), thicc)
    return av.VideoFrame.from_ndarray(frame,format="bgr24")
def main():
  webrtc_streamer(key='sample',video_frame_callback=callback)
if __name__== '__main__':
    main()

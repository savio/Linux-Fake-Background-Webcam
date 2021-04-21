# import the necessary packages
from imutils.video import VideoStream
import PIL
from PIL import Image,ImageTk
import cv2
import tkinter as tk 
import datetime
import imutils
import time
import cv2
import winsound

width, height = 1920, 1080
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FOCUS, 12)

firstFrame = None
min_area = 1500

camera_ativa = True

habilitar_gravar = False
habilitar_audio = True

def change_focus(v):
    cap.set(cv2.CAP_PROP_FOCUS, int(v))

def change_camera(v):
    global cap
    global camera_ativa
    global width, height

    camera_ativa = False
    cap.release()
    cap = cv2.VideoCapture(int(v))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FOCUS, 12)

    camera_ativa = True
    show_frame()

def keydown(e, root):
    global habilitar_gravar
    global habilitar_audio

    if (e.char == 'q'):
        print('Habilitando gravação')
        habilitar_gravar = True

    if (e.char == 'p'):
        print('Desabilitando gravação')
        habilitar_gravar = False
    
    if (e.char == 'r'):
        root.geometry("1280x870+320+80")
    
    if (e.char == 's'):
        habilitar_audio = not habilitar_audio
        print('Audio %s' % (habilitar_audio))

    if (e.char == 'm'):
        root.geometry("320x320+1520+80")
    if (e.char == '1'):
        cap.set(cv2.CAP_PROP_FOCUS, 6)
    if (e.char == '2'):
        cap.set(cv2.CAP_PROP_FOCUS, 7)
    if (e.char == '3'):
        cap.set(cv2.CAP_PROP_FOCUS, 8)
    if (e.char == '4'):
        cap.set(cv2.CAP_PROP_FOCUS, 9)
    if (e.char == '5'):
        cap.set(cv2.CAP_PROP_FOCUS, 10)
    if (e.char == '6'):
        cap.set(cv2.CAP_PROP_FOCUS, 11)
    if (e.char == '7'):
        cap.set(cv2.CAP_PROP_FOCUS, 12)
    if (e.char == '8'):
        cap.set(cv2.CAP_PROP_FOCUS, 13)
    if (e.char == '9'):
        cap.set(cv2.CAP_PROP_FOCUS, 14)
    if (e.char == '0'):
        cap.set(cv2.CAP_PROP_FOCUS, 15)

root = tk.Tk()
root.bind('<Escape>', lambda e: root.quit()) 
root.bind("<KeyPress>", lambda e: keydown(e, root))
root.attributes('-topmost', True)
lmain = tk.Label(root)
lmain.pack()
camera = tk.Scale(root, label='Camera', from_=0, to=2, orient=tk.HORIZONTAL, length=400, showvalue=0,tickinterval=1, resolution=1, command=change_camera)
camera.set(0)
camera.pack()
s = tk.Scale(root, label='Focus', from_=0, to=20, orient=tk.HORIZONTAL, length=400, showvalue=0,tickinterval=1, resolution=1, command=change_focus)
s.set(12)
s.pack()


count = 0

gravar = False
num_frames = 0

fourcc = cv2.VideoWriter_fourcc(*'DIVX')
count_video = 0
out = None

def show_frame():
    global width
    global height
    global firstFrame
    global min_area
    global count
    global out
    global fourcc
    global count_video
    global gravar
    global num_frames
    global camera_ativa
    global habilitar_audio

    if camera_ativa:
        ret, frame = cap.read()
        if ret:
            # grab the current frame and initialize the Detectado/Não Detectado
            # text
            text = "Nao Detectado"
            # if the frame could not be grabbed, then we have reached the end
            # of the video
            if frame is None:
                return
            # resize the frame, convert it to grayscale, and blur it
            #frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            # if the first frame is None, initialize it
            if firstFrame is None or count > 10:
                count = 0
                firstFrame = gray
                lmain.after(10, show_frame)
                return

            
            # compute the absolute difference between the current frame and
            # first frame
            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            # loop over the contours
            frameOriginal = frame.copy()
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < min_area:
                    continue
                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Detectado"
                break

            if text == "Detectado" and habilitar_gravar and gravar == False:
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                out = cv2.VideoWriter('videos/video-' + str(count_video) + '.avi',fourcc, 20.0, (w,h))
                gravar = True
                num_frames = 0

            if habilitar_gravar and gravar and num_frames > 200:
                gravar = False
                out.release()
                count_video = count_video + 1
            
            if habilitar_gravar and gravar:
                out.write(frameOriginal)
                num_frames = num_frames + 1
                
            if habilitar_gravar == False and gravar:
                gravar = False
                out.release()
                count_video = count_video + 1

            # draw the text and timestamp on the frame
            cor = (0, 255, 0) if habilitar_gravar else (0, 0, 255)
            cv2.putText(frame, "Gravacao Habilitada: {}".format(str(habilitar_gravar)), (frame.shape[1] - 230, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 2)

            if text == "Detectado":
                cor2 = (0, 255, 0)
                if habilitar_audio:
                    winsound.Beep(600, 50)  
            else:
                cor2 = (0, 0, 255)

            cv2.putText(frame, "Movimento: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor2, 2)
            cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = PIL.Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            lmain.after(5, show_frame)

            count = count + 1



show_frame()
root.mainloop()
# cleanup the camera and close any open windows
if out:
    out.release()
cap.release()
cv2.destroyAllWindows()
# import the necessary packages
from imutils.video import VideoStream
import PIL
from PIL import Image,ImageTk
import cv2
from tkinter import *
import datetime
import imutils
import time
import cv2
import winsound

width, height = 1920, 1080
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FOCUS, 5)

firstFrame = None
min_area = 500

habilitar_gravar = False

def keydown(e):
    global habilitar_gravar
    if (e.char == 'q'):
        print('Habilitando gravação')
        habilitar_gravar = True

    if (e.char == 'p'):
        print('Desabilitando gravação')
        habilitar_gravar = False

root = Tk()
root.bind('<Escape>', lambda e: root.quit()) 
root.bind("<KeyPress>", keydown)
lmain = Label(root)
lmain.pack()

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

    ret, frame = cap.read()
    if ret:
        # grab the current frame and initialize the occupied/unoccupied
        # text
        text = "Unoccupied"
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
            text = "Occupied"
            winsound.Beep(600, 50)
            break

        if text == "Occupied" and habilitar_gravar and gravar == False:
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

        # draw the text and timestamp on the frame
        cor = (0, 255, 0) if habilitar_gravar else (0, 0, 255)
        cv2.putText(frame, "Gravacao Habilitada: {}".format(str(habilitar_gravar)), (frame.shape[1] - 230, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 2)
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = PIL.Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(10, show_frame)

        count = count + 1

        # cv2.imshow("Thresh", thresh)
        # cv2.imshow("Frame Delta", frameDelta)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            print('pressed')
            return



show_frame()
root.mainloop()
# cleanup the camera and close any open windows
if out:
    out.release()
cap.release()
cv2.destroyAllWindows()
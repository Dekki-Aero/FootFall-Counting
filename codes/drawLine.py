import cv2#,imutils
import time
# from codes.config import config

def image_resize(image,width = None, height = None):
    if width is None and height is None: return image
    #ar = width/height
    aspect_ratio = float(image.shape[1])/float(image.shape[0])
    if width is None:
        window_width = height * aspect_ratio
        image = cv2.resize(image, (int(window_width),int(height)))
    else:
        window_height = width/aspect_ratio
        image = cv2.resize(image, (int(width),int(window_height)))
    return image

def draw_line_with_drag(event, x, y, flags, frame):
    global img,fnl, strt ,ix, iy, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y
        strt = ix, iy
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img = frame.copy()
            cv2.line(img, pt1=(ix, iy),
                          pt2=(x, y),
                          color=(0, 255, 255),
                          thickness=2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.line(img, pt1=(ix, iy),
                      pt2=(x, y),
                      color=(0, 255, 255),
                      thickness=2)
        fnl = x,y

def getBoundry(config,vs,width,logger,INPUT_VIDEO):
    reDraw = config['boundry'].getboolean('re_draw')
    if reDraw:
        global drawing,ix,iy,img
        vdoStatus, frame = vs.read()
        while True:
            if vdoStatus: break
            else:
                logger.warning("Unable to get video stream")
                vs = cv2.VideoCapture(INPUT_VIDEO, cv2.CAP_FFMPEG)
                logger.info("Pausing for 20 Sec ...")
                time.sleep(20)
                n+=1
            if n==5: 
                logger.warning("Unable to get video stream")
                return -1
        # if vdoStatus:
        #     frame = image_resize(image=frame,width=width)

        ix,iy = -1,-1
        drawing = False
        img = frame.copy()
        cv2.namedWindow(winname="Title of Popup Window")
        cv2.setMouseCallback("Title of Popup Window",
                             draw_line_with_drag,param=frame)

        while True:
            cv2.imshow("Title of Popup Window", img)

            if cv2.waitKey(10) == 27:
                break
        cv2.destroyAllWindows()
        # config.add_section('boundry')
        (ax,ay),(bx,by) = sorted([strt,fnl])
        config.set('boundry','pts',f"{ax},{ay},{bx},{by}")
        config.write(open('config.txt','w'))
    else:
        ax,ay,bx,by = list(map(int,config['boundry'].get('pts').split(',')))
    return (ax,ay),(bx,by)
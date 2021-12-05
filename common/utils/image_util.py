from keras.preprocessing import image
from datetime import date, datetime
from os import path, times
from time import sleep
import common.utils.classification_util as classificationModule
import numpy as np
import cv2
import importlib
import sys

found = False
spam_loader = importlib.util.find_spec('picamera')

if spam_loader is not None:
    from picamera import PiCamera #type: ignore
    found = True

class ImageUtil:
    @staticmethod
    def predictImageTensorflow(image, tensorflowModel):       
        np.set_printoptions(suppress=True)
        image = np.vstack([image])
        result = tensorflowModel.predict(image, batch_size=64)
        
        return result

    @staticmethod
    def predictImageTensorflowLite(image, tensorflowLiteModel):       
        inputDetails = tensorflowLiteModel.get_input_details()    
        outputDetails = tensorflowLiteModel.get_output_details()

        tensorflowLiteModel.set_tensor(inputDetails[0]['index'], image)
        tensorflowLiteModel.invoke()

        return tensorflowLiteModel.get_tensor(outputDetails[0]['index'])

    @staticmethod
    def captureImage(cam, metrics = False, showPreview = False, framerate = 10):
        if(found):
            return ImageUtil.__callPicameraCapture(metrics, showPreview, framerate)
        return ImageUtil.__callOpenCVCapture(cam, metrics, showPreview, framerate)

    @staticmethod
    def resizeImage(image, imageSize, colorScale):
        return ImageUtil.__resizeImage(image, imageSize, colorScale)

    @staticmethod
    def saveImage(image, fileName: str, savePath = None):
        experimentPath = './experiments/' + savePath
        if(savePath != None and path.isdir(experimentPath)):
            cv2.imwrite(experimentPath + '/' + fileName + ".jpg", image)

    @staticmethod
    def writeTextInImage(image, org, imageText: str, fontColor = (0,0,0)):
        if(imageText != None):
            font                   = cv2.FONT_HERSHEY_SIMPLEX
            fontScale              = 1
            thickness              = 2
            lineType               = 2
            
            cv2.putText(image, imageText, org, font, fontScale, fontColor, thickness, lineType)
        
        return image

    @staticmethod
    def openAndResizedImage(path, imageSize, colorScale, metrics = False, showPreview = False):
        timeStart = datetime.now()
        image = cv2.imread(path)
        if(showPreview):
            ImageUtil.__showImage(image, 1)
        resizedImage = ImageUtil.__resizeImage(image, imageSize, colorScale)
        timeEnd = datetime.now()
        if(metrics):
            classificationModule.ClassificationUtil.calculeClassificationElapsedTime(timeStart, timeEnd, "Open Image")
        return resizedImage

    def __callPicameraCapture(metrics = False, showPreview = False, framerate = 10):
        timeStart = datetime.now()
        
        camera = PiCamera()
        camera.resolution = (640 , 480)
        camera.framerate = 10
        
        #Capture opencv object
        output = np.empty((480 * 640 * 3,), dtype=np.uint8)
        camera.capture(output, 'bgr')
        output = output.reshape((480, 640, 3))
        
        if(showPreview):
            ImageUtil.__showImage(output, 60)
        
        loadImageTime = (datetime.now() - timeStart).microseconds / 1000000
        ImageUtil.__waitFrameTime(framerate, loadImageTime)
        
        timeEnd = datetime.now()
        
        if(metrics):
            classificationModule.ClassificationUtil.calculeClassificationElapsedTime(timeStart, timeEnd, "Capture Image")
        
        camera.close()
        
        return output
    
    def __callOpenCVCapture(cam, metrics = False, showPreview = False, framerate = 10):
        timeStart = datetime.now()

        camImage = cam.read()
        if(showPreview):
            ImageUtil.__showImage(camImage[1], 60)

        loadImageTime = (datetime.now() - timeStart).microseconds / 1000000
        ImageUtil.__waitFrameTime(framerate, loadImageTime)

        timeEnd = datetime.now()

        if(metrics):
            classificationModule.ClassificationUtil.calculeClassificationElapsedTime(timeStart, timeEnd, "Capture Image")

        return camImage[1]

    def __waitFrameTime(framerate, imageCaptureTime):
        total = (1/framerate) - imageCaptureTime
        if(total > 0):
            sleep(total) 

    def __resizeImage(imageToResize, imageSize, colorScale):
        imageToResize = cv2.resize(imageToResize, imageSize)
        imageToResize = cv2.cvtColor(imageToResize, colorScale)
        x = image.img_to_array(imageToResize)
        x = np.expand_dims(x, axis=0)

        return x

    def __showImage(imageToShow, waitTime):
        imageToShow = cv2.resize(imageToShow, (480,720))
        cv2.imshow('Imagem', imageToShow)
        cv2.waitKey(waitTime)

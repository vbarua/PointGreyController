from PGTypes import *
from ctypes import *

FCDriver = CDLL('FlyCapture2_C')


#class FlyCaptureError(Exception):
	

def handleError(errorCode):
	if errorCode:
		print errorCode
		print fc2ErrorCodeStrings[errorCode]
		
		
class PointGreyController(object):
	
	def __init__(self):
		context = fc2Context()
		handleError(FCDriver.fc2CreateContext(byref(context)))		
		self.context = context
		guid = fc2PGRGuid()
		handleError(FCDriver.fc2GetCameraFromIndex(context, 0, byref(guid)))
		self.guid = guid
		handleError(FCDriver.fc2Connect(context, byref(guid)))
		
	def start(self):
		context = self.context
		handleError(FCDriver.fc2StartCapture(context))

	def enableTrigger(self):
		context = self.context
		triggerMode = fc2TriggerMode()
		triggerMode.onOff = True
		triggerMode.mode = 0;
		triggerMode.parameter = 0;
		triggerMode.source = 7;
		handleError(FCDriver.fc2SetTriggerMode(context, byref(triggerMode)))

	def initializeImage(self):
		img = fc2Image()
		handleError(FCDriver.fc2CreateImage(byref(img)))
		return img
	
	def retrieveImage(self, img):
		context = self.context
		handleError(FCDriver.fc2RetrieveBuffer(context, byref(img)))
		
	def convertImg(self, rawImage):
		convertedImage = fc2Image()
		handleError(FCDriver.fc2CreateImage(byref(convertedImage)))
		handleError(FCDriver.fc2ConvertImageTo(fc2PixelFormat['BGR'], byref(rawImage), byref(convertedImage)))
		return convertedImage
		
	def saveImage(self, img, fname = 'test.png'):
		fname = c_char_p(fname)
		handleError(FCDriver.fc2SaveImage(byref(img), fname, 6))	
		
	def stop(self):
		context = self.context
		handleError(FCDriver.fc2StopCapture(context))
		handleError(FCDriver.fc2DestroyContext(context))

PGC = PointGreyController()
PGC.start()
raw = PGC.initializeImage()
print type(raw)
PGC.retrieveImage(raw)
converted = PGC.convertImg(raw)
print type(converted)
PGC.saveImage(converted)
PGC.stop()


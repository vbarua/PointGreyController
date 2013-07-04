from PGTypes import *
from threading import Thread
from ctypes import *

# http://www.ptgrey.com/support/downloads/documents/flycapture/Doxygen/html/group___enumerations.html#g7fcfd5d4f93c612885ac16a99ee04647

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

	def setConfig(self):
		config = fc2Config()
		config.numBuffers = 4
		config.numImageNotifications = 1
		config.grabTimeout = -1
		config.grabMode = fc2GrabMode['BUFFER_FRAMES']
		config.isochBusSpeed = fc2BusSpeed['SPEED_UNKNOWN']
		config.asyncBusSpeed = fc2BusSpeed['ANY']
		config.bandwidthAllocation = fc2BandwidthAllocation['ON']
		
	def getConfig(self):
		context = self.context
		config = fc2Config()
		handleError(FCDriver.fc2GetConfiguration(context, byref(config)))
		return config	
	
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
	
	def fireSoftwareTrigger(self):
		context = self.context
		handleError(FCDriver.fc2FireSoftwareTrigger(context))
		
	def stop(self):
		context = self.context
		handleError(FCDriver.fc2StopCapture(context))
		handleError(FCDriver.fc2DestroyContext(context))

class PointGreyTriggerThread(Thread):
	def __init__(self, PGController, imgArray):
		Thread.__init__(self)
		self.PGC = PGController
		self.imgArray = imgArray
		
	def run(self):
		PGC = self.PGC
		imgArray = self.imgArray
		for img in imgArray:
			print "Retrieving"
			PGC.retrieveImage(img)

# PGC = PointGreyController()
# PGC.setConfig()
# PGC.start()
# PGC.enableTrigger()
# raw1 = PGC.initializeImage()
# raw2 = PGC.initializeImage()
# raw_input('Waiting')
# PGC.fireSoftwareTrigger()
# raw_input('Waiting')
# PGC.fireSoftwareTrigger()
# PGC.retrieveImage(raw1)
# PGC.retrieveImage(raw2)
# con1 = PGC.convertImg(raw1)
# con2 = PGC.convertImg(raw2)
# PGC.saveImage(con1, 'img1.png')
# PGC.saveImage(con2, 'img2.png')
# PGC.stop()


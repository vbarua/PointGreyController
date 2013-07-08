from PGTypes import *
from threading import Thread
from ctypes import *
from struct import pack, unpack

# http://www.ptgrey.com/support/downloads/documents/flycapture/Doxygen/html/index.html
FCDriver = CDLL('FlyCapture2_C')


# ----- Conversion Functions	----- #

def hexifier(fl):
	# http://stackoverflow.com/questions/1922771/python-obtain-manipulate-as-integers-bit-patterns-of-floats
	s = pack('>f', fl)
	''.join('%2.2x' % ord(c) for c in s)
	i = unpack('>l', s)[0]
	return i
	
def floatifier(h):
	neg = h & 0x80000000
	h = h & 0x7fffffff
	s = pack('>l', h)
	''.join('%2.2x' % ord(c) for c in s)
	i = unpack('>f', s)[0]
	if neg:
		i = -i
	return i
	
# ----- Region of Interest ----- #

class ROIError(Exception):
	"""For errors in setting the Region of Interest"""
	def __init__(self, value, issueStr):
		self.issueStr = issueStr
		
	def __str__(self):
		return repr(self.issueStr + str(value))

class ROI(object):
	"""Defines the region of interest of the camera."""
	
	def __init__(self):
		self.posLeft = 0
		self.posTop = 0
		self.width = 960
		self.height = 1280
	
	def __str__(self):
		return 'Left: %d, Top: %d, Width: %d, Height: %d' % (self.posLeft, self.posTop, self.width, self.height)
	
	def checkValues(self):
		"""Verifies validity of ROI Values for Flea2 Camera."""
		posTop = self.posTop	#Pixels from left to start ROI.
		posLeft = self.posLeft	#Pixels from top to start ROI.
		width = self.width		#Width (in pixels) of the ROI.
		height = self.height	#Height (in pixels) of the ROI.
		if not(0 <= posTop < 960):
			raise ROIError(posTop, 'Top must be between 0 and 960. Currently ') 
		if not(0 <= posLeft < 1280):
			raise ROIError(posLeft, 'Left must be between 0 and 1280. Currently ')
		if not(0 <= width <= 960):
			raise ROIError(width, 'Width must be between 0 and 960. Currently ') 
		if not(0 <= height <= 1280):
			raise ROIError(posTop, 'Height must be between 0 and 960. Currently ') 
		if not(0 < posTop + height <= 960):
			raise ROIError(posTop + height, 'Top + height must be <= 960. Currently ')
		if not(0< posLeft + width <= 1280):
			raise 0 < ROIError(posLeft + width, 'Left + width must be <=1280. Currently ')
	
	def setROI(self, posLeft, posTop, width, height):
		"""Sets the ROI parameters explicitly."""
		self.posLeft = posLeft - posLeft % 2	#Pixels from left to start ROI.
		self.posTop = posTop - posTop % 2 		#Pixels from top to start ROI.
		self.width = int(ceil(width / 8.) * 8) 	#Width (in pixels) of the ROI.
		self.height = height + height % 2		#Height (in pixels) of the ROI.
		self.checkValues()
	
	def setROICenter(center, width, height):
		"""
		Sets the ROI parameters based on where the image center should be along
		with the width and height. center is a tuple of the form (x, y).
		"""
		x = center(0)
		y = center(1)
		self.width = int(ceil(width / 8.) * 8) 	#Width (in pixels) of the ROI.
		self.height = height + height % 2		#Height (in pixels) of the ROI.
		hWidth = self.width/2
		hHeight = self.height/2
		l = x - hWidth
		t = y - hHight
		self.posLeft = l - l % 2
		self.posTop = t - t % 2
		self.checkValues()	
	
# ----- Point Grey Controller ----- #

def handleError(errorCode):
	if errorCode:
		raise flyCaptureError(errorCode)
		
class propertyError(Exception):
	"""For errors when setting camera property values"""
	def __init__(self, name, value, min, max, units):
		self.value = value
		self.min = min
		self.max = max
		self.units = units
	
	def __str__(self):
		return repr('%s %f %s is outside of range %f to %f.' % self.name, self.value, self.units, self.min, self.max, self.units)		

class flyCaptureError(Exception):
	'''For errors returned from FlyCapture2 API calls'''
	def __init__(self, errorCode):
		self.errorCode = errorCode
		self.msg = fc2ErrorCodeStrings[self.errorCode]
		
	def __str__(self):
		
		return repr(self.msg)
	
class PointGreyController(object):
	
	def __init__(self, numOfImages = 4, expTime_ms = 15, gain = 0, roi = ROI()):
		self.numOfImages = numOfImages
		self.expTime_ms = expTime_ms
		self.gain = 0
		self.roi = False
		
		context = fc2Context()
		handleError(FCDriver.fc2CreateContext(byref(context)))		
		self.context = context
		guid = fc2PGRGuid()
		handleError(FCDriver.fc2GetCameraFromIndex(context, 0, byref(guid)))
		self.guid = guid
		handleError(FCDriver.fc2Connect(context, byref(guid)))
		
		# Re-initialize and re-power camera.
		self.setRegister(fc2Register['Initialize'], 0x80000000)
		self.setRegister(fc2Register['Power'], 0x80000000)
		
		# Disables unused camera settings.
		self.setRegister(fc2Register['AutoExposure'], 0x40000000)
		self.setRegister(fc2Register['Sharpness'], 0x40000000) 
		self.setRegister(fc2Register['Gamma'], 0x40000000) 
		self.setRegister(fc2Register['Pan'], 0x40000000)
		self.setRegister(fc2Register['Tilt'], 0x40000000)

		# Initialize Gain and Shutter  settings.
		self.setRegister(fc2Register['Gain'], 0x42000000)
		self.setGain(gain)
		self.setRegister(fc2Register['Shutter'], 0x42000000)
		self.setExposureTime(expTime_ms)
		
		# Set camera region of interest.
		self.setROI(roi)
		
			
		
		# Set the number of images to collect.
		self.setNumberOfImages(numOfImages)
		
	def start(self):
		context = self.context
		handleError(FCDriver.fc2StartCapture(context))

	def setROI(self, roi):
		context = self.context
		imSet = fc2Format7ImageSettings()
		imSet.mode = 0
		imSet.offsetX = roi.posLeft 
		imSet.offsetY = roi.posTop
		imSet.width = roi.width
		imSet.height = roi.height
		imSet.pixelFormat = fc2PixelFormat['MONO8'] 
		percentSpeed = c_float(50)
		handleError(FCDriver.fc2SetFormat7Configuration(context, byref(imSet), percentSpeed))
	
	def enableTrigger(self):
		context = self.context
		triggerMode = fc2TriggerMode()
		triggerMode.onOff = True
		triggerMode.mode = 0;
		triggerMode.parameter = 0;
		triggerMode.source = 7;
		handleError(FCDriver.fc2SetTriggerMode(context, byref(triggerMode)))

	def getConfig(self):
		context = self.context
		config = fc2Config()
		handleError(FCDriver.fc2GetConfiguration(context, byref(config)))
		return config

	def setNumberOfImages(self, numOfImages):
		config = fc2Config()
		config.numBuffers = 4
		config.numImageNotifications = 1
		config.grabTimeout = -1
		config.grabMode = fc2GrabMode['BUFFER_FRAMES']
		config.isochBusSpeed = fc2BusSpeed['SPEED_UNKNOWN']
		config.asyncBusSpeed = fc2BusSpeed['ANY']
		config.bandwidthAllocation = fc2BandwidthAllocation['ON']
		
	def setExposureTime(self, ms):
		min = 1000 * floatifier(self.getRegister(0x910))
		max = 1000 * floatifier(self.getRegister(0x914))
		if min < ms < max:
			s = float(ms / 1000.)
			s = hexifier(s)
			self.setRegister(0x918, s)
		else:
			raise propertyError('Exposure time', ms, min, max, 'ms')
		
	def getExposureTime(self):
		t = self.getRegister(0x918)
		t = 1000. * floatifier(t)
		return t
		
	def setGain(self, db):
		min = floatifier(self.getRegister(0x920))
		max = floatifier(self.getRegister(0x924))
		if min < db < max:
			db = float(db)
			db = hexifier(db)
			self.setRegister(0x928, db)
		else:
			raise propertyError('Gain', db, min, max, 'db')
	
	def getGain(self):
		g = self.getRegister(0x928)
		g = floatifier(g)
		return g
		
	def getImageSettings(self):
		context = self.context
		packetSize = c_uint()
		percentage = c_float()
		imageSettings = fc2Format7ImageSettings()
		handleError(FCDriver.fc2GetFormat7Configuration(context, byref(imageSettings), byref(packetSize), byref(percentage)))
		for (key, val) in imageSettings.__fields__:
			print key, getattr(imageSettings, key)
		return imageSettings	
	
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
	
	def getRegister(self, addr):
		context = self.context
		val = c_ulong()
		handleError(FCDriver.fc2ReadRegister(context, addr, byref(val)))
		return val.value
	
	def setRegister(self, addr, val):
		context = self.context
		val = c_uint(val)
		handleError(FCDriver.fc2WriteRegister(context, addr, val))

# 	def getProperty(self, propertyType):
# 		context = self.context
# 		property = fc2Property()
# 		property.type = propertyType
# 		handleError(FCDriver.fc2GetProperty(context, byref(property)))
# 		print type(property)
# 		return property 
	
# 	def printProperty(self, propertyType):
# 		property = self.getProperty(propertyType)
# 		for (key, val) in property._fields_:
# 			t = getattr(property, key)
# 			print key, t, type(t)
	
# 	def disableProperty(self, propertyType):
# 		context = self.context
# 		property = self.getProperty(propertyType)
# 		property.onOff = True
# 		property.onePush = False
# 		property.autoManualMode = False
# 		handleError(FCDriver.fc2SetProperty(context, byref(property)))
 	
# 	def setProperty(self, propertyType, value):
# 		context = self.context
# 		property = fc2Property()
# 		property.type = c_int(propertyType)
# 		property.absControl = True
# 		property.onePush = False
# 		property.autoManualMode = False
# 		property.absValue = c_float(value)
# 		handleError(FCDriver.fc2SetProperty(context, byref(property)))
# 	
# 	def getPropertyInfo(self, propertyType):
# 		context = self.context
# 		info = fc2PropertyInfo()
# 		info.type = propertyType
# 		print "BEFORE"
# 		for (key, val) in info._fields_:
# 			print key, getattr(info, key)
# 		print "AFTER"
# 		handleError(FCDriver.fc2GetPropertyInfo(context, byref(info)))
# 		for (key, val) in info._fields_:
# 			print key, getattr(info, key)
# 		return info


roi = ROI()		
PGC = PointGreyController()
# PGC.getImageSettings()



# Used to take images
PGC.start()
PGC.enableTrigger()
raw1 = PGC.initializeImage()
raw2 = PGC.initializeImage()
raw_input('Waiting')
PGC.fireSoftwareTrigger()
raw_input('Waiting')
PGC.fireSoftwareTrigger()
PGC.retrieveImage(raw1)
PGC.retrieveImage(raw2)
con1 = PGC.convertImg(raw1)
con2 = PGC.convertImg(raw2)
PGC.saveImage(con1, 'img1.png')
PGC.saveImage(con2, 'img2.png')
PGC.stop()




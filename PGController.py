from PGTypes import *
from threading import Thread
from ctypes import *
from struct import pack, unpack

# http://www.ptgrey.com/support/downloads/documents/flycapture/Doxygen/html/index.html
FCDriver = CDLL('FlyCapture2_C')


#class FlyCaptureError(Exception):
	

def handleError(errorCode):
	if errorCode:
		print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
		print errorCode
		print fc2ErrorCodeStrings[errorCode]
		
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
		
class PointGreyController(object):
	
	def __init__(self):
		context = fc2Context()
		handleError(FCDriver.fc2CreateContext(byref(context)))		
		self.context = context
		guid = fc2PGRGuid()
		handleError(FCDriver.fc2GetCameraFromIndex(context, 0, byref(guid)))
		self.guid = guid
		handleError(FCDriver.fc2Connect(context, byref(guid)))
		
		#
		self.setRegister(fc2Register['Initialize'], 0x80000000)
		self.setRegister(fc2Register['Power'], 0x80000000)
		
		# Disables unused camera settings.
		self.setRegister(fc2Register['AutoExposure'], 0x40000000)
		self.setRegister(fc2Register['Sharpness'], 0x40000000) 
		self.setRegister(fc2Register['Gamma'], 0x40000000) 
		self.setRegister(fc2Register['Pan'], 0x40000000)
		self.setRegister(fc2Register['Tilt'], 0x40000000)

		# 
		self.setRegister(fc2Register['Gain'], 0x42000000)
		self.setRegister(fc2Register['Shutter'], 0x42000000)
		
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

	def getConfig(self):
		context = self.context
		config = fc2Config()
		handleError(FCDriver.fc2GetConfiguration(context, byref(config)))
		return config

	def setConfig(self):
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
		
		print min, max
		if min < ms < max:
			s = float(ms / 1000.)
			s = hexifier(s)
			self.setRegister(0x918, s)
		else:
			print "Exposure time must be between blah"	
		
	def getExposureTime(self):
		t = self.getRegister(0x918)
		t = 1000. * floatifier(t)
		return t
		
	def setGain(self, db):
		min = floatifier(self.getRegister(0x920))
		max = floatifier(self.getRegister(0x924))
		
		print min, max
		if min < db < max:
			db = float(db)
			db = hexifier(db)
			self.setRegister(0x928, db)
		else:
			print "Gain must be between blah"	


	
# 	def setGain(self, db):
# 		if -6.264 < db < 24:
# 			s = float(ms / 1000.)
# 			s = hexifier(s)
# 			self.setRegister(0x918, s)
# 		else:
# 			print "Exposure time must be between blah"
		
	def getImageSettings(self):
		context = self.context
		packetSize = c_uint()
		percentage = c_float()
		imageSettings = fc2Format7ImageSettings()
		handleError(FCDriver.fc2GetFormat7Configuration(context, byref(imageSettings), byref(packetSize), byref(percentage)))
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
		
PGC = PointGreyController()
PGC.setGain(10.3)


# r = PGC.getRegister(0x720)
# r = r * 4
# print hex(r)
# r = r & 0x0fffffff
# print hex(r)



# print "PROPERTY"
#PGC.printProperty(13)

#PGC.getProperty(13)
# PGC.setProperty(13, 7)


# PGC.setExposureTime(0.1)
# PGC.getExposureTime()

#imSet = PGC.getImageSettings()
#print imSet.mode
#print imSet.offsetX
#print imSet.offsetY
#print imSet.width
#print imSet.height
#print hex(c_uint(imSet.pixelFormat).value)



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


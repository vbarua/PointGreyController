from PGTypes import *
from threading import Thread
from ctypes import *
from struct import pack, unpack
from math import ceil
import time

FCDriver = CDLL('FlyCapture2_C')
# FlyCapture2 C Documentation:
# http://www.ptgrey.com/support/downloads/documents/flycapture/Doxygen/html/index.html


# ----- Conversion Functions ----- #

def hexifier(fl):
	'''
	Converts a floating point number into a number corresponding to its
	hexadecimal/binary representation. Used to convert settings values for input
	into the camera registers.
	'''
	# Taken from:
	# http://stackoverflow.com/questions/1922771/python-obtain-manipulate-as-integers-bit-patterns-of-floats
	s = pack('>f', fl)
	''.join('%2.2x' % ord(c) for c in s)
	i = unpack('>l', s)[0]
	return i
	
def floatifier(h):
	'''
	Converts a hexademical value returned by the camera registers to a floating
	point number.
	'''
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

# ----- Timestamp ----- #

class Timestamp(object):
	"""Used to store and decode image timestamps."""

	secondsPerCount = 1./8000.
	countsPerOffset = 1./3072.
	
	def __init__(self, s, c, o):
		self.seconds = s
		self.count = c
		self.offset = o
	
	def decodeTime(self):
		"""Converts timestamp to time in seconds based on FlyCapture Documentation."""
		return self.seconds + (self.count+self.offset*self.countsPerOffset)*self.secondsPerCount
		
# ----- Point Grey Controller ----- #

def handleError(errorCode):
	'''
	Wrapper for FlyCapture2 API function calls which handles the error
	codes it returns.
	'''
	if errorCode:
		raise flyCaptureError(errorCode)
		
class propertyError(Exception):
	"""For errors when setting camera property values"""
	def __init__(self, name, value, min, max, units):
		msg = '%s %f %s is outside of range %f to %f.' % (name, value, units, min, max)
		
	def __str__(self):
		return repr(self.msg)		

class flyCaptureError(Exception):
	'''For errors returned from FlyCapture2 API calls'''
	def __init__(self, errorCode):
		self.errorCode = errorCode
		self.msg = fc2ErrorCodeStrings[self.errorCode]
		
	def __str__(self):
		return repr(self.msg)
	
class PointGreyController(object):
	
	def __init__(self, numOfImages = 4, expTime_ms = 15, gain = 0, roi = False):
		self.numOfImages = numOfImages
		self.expTime_ms = expTime_ms
		self.gain = 0
		self.roi = roi
		
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
		
		# Set camera configuration and enable embedded image timestamps
		self.setConfig(numOfImages)
		self.enableTimestamps()
		
		# Set camera region of interest.
		if roi:
			self.setImageSettings(roi)
		
		# Disables unused camera settings.
		self.setRegister(fc2Register['AutoExposure'], 0x40000000)
		self.setRegister(fc2Register['Sharpness'], 0x40000000) 
		self.setRegister(fc2Register['Gamma'], 0x40000000) 
		self.setRegister(fc2Register['Pan'], 0x40000000)
		self.setRegister(fc2Register['Tilt'], 0x40000000)

		# Initialize Gain and Shutter settings.
		self.setRegister(fc2Register['Gain'], 0x42000000)
		self.setGain(gain)
		self.setRegister(fc2Register['Shutter'], 0x42000000)
		self.setExposureTime(expTime_ms)
		
		# Initialise data storage structures
		self.setImageBuffer(numOfImages)
		
	def start(self):
		'''Readies camera to capture images when triggered.'''
		context = self.context
		handleError(FCDriver.fc2StartCapture(context))
		self.clearBuffer()
		
	def stop(self):
		'''Stop collecting images and disassociate context from camera.'''
		context = self.context
		handleError(FCDriver.fc2StopCapture(context))
		handleError(FCDriver.fc2DestroyContext(context))
	
	def setImageBuffer(self, numOfImages):
		'''
		Sets up the image buffers to which the camera will save data, along
		with the associated timestamp data.
		'''
		self.timestamps = [float()]*numOfImages
		self.rawImageData = [self.initializeImage() for _ in range(numOfImages)]
		self.conImageData = [self.initializeImage() for _ in range(numOfImages)]
		
# ----- Save Functions
	
	def saveRAWImages(self, fNameFormat = 'rawImage_%03d.raw'):
		'''Saves the images collected using the raw format.'''
		images = self.conImageData
		for i in range(len(images)):
			im = images[i]
			fname = fNameFormat % i
			fname = c_char_p(fname)
			handleError(FCDriver.fc2SaveImage(byref(im), fname, fc2ImageFileFormat['RAW']))	
		
	def savePNGImages(self, fNameFormat = 'image_%03d.png'):
		'''Save the images collected using the png format.'''
		images = self.conImageData
		for i in range(len(images)):
			im = images[i]
			fname = fNameFormat % i
			fname = c_char_p(fname)
			handleError(FCDriver.fc2SaveImage(byref(im), fname, fc2ImageFileFormat['PNG']))	
		
	def saveLog(self, fpath = 'log.txt'):
		"""Creates and saves log file for image collection run"""
		timestamps = self.timestamps
		outfile = open(fpath, 'w')
		outfile.write('Collection Time: %s\n' % (time.strftime("%y%m%d_%H%M%S")))
		outfile.write('Exposure Time: %d ms, Gain: %d dB\n' % (self.expTime_ms, self.gain))
		if self.roi:
			outfile.write(str(self.roi))
		else:
			outfile.write('Full Region Utilized (1280x960)')
		outfile.write('\n\nImage #: Time Since First Image (ms) - Processing Status\n')
		for i in range(len(timestamps)): 
			outfile.write('Image %d: {%.14f}\n' % (i, timestamps[i]))
		outfile.close()	

# ----- Settings Functions
	
	def getExposureTime(self):
		'''Get camera exposure time in ms.'''
		t = self.getRegister(0x918)
		t = 1000. * floatifier(t)
		return t
	
	def setExposureTime(self, ms):
		'''Set camera exposure time. Input is in ms.'''
		min = 1000 * floatifier(self.getRegister(0x910))
		max = 1000 * floatifier(self.getRegister(0x914))
		if min < ms < max:
			s = float(ms / 1000.)
			s = hexifier(s)
			self.setRegister(0x918, s)
		else:
			raise propertyError('Exposure time', ms, min, max, 'ms')
		
	def getGain(self):
		'''Get camera gain level in db.'''
		g = self.getRegister(0x928)
		g = floatifier(g)
		return g
		
	def setGain(self, db):
		'''Set camera gain leve in db.'''
		min = floatifier(self.getRegister(0x920))
		max = floatifier(self.getRegister(0x924))
		if min < db < max:
			db = float(db)
			db = hexifier(db)
			self.setRegister(0x928, db)
		else:
			raise propertyError('Gain', db, min, max, 'db')

# ----- Image Handling Functions
	
	def initializeImage(self):
		'''Initializes an fc2Image object for use with camera.'''
		img = fc2Image()
		handleError(FCDriver.fc2CreateImage(byref(img)))
		return img
	
	def retrieveImages(self):
		'''Retrieves all of the images collected by the camera.'''
		context = self.context
		rawDat = self.rawImageData
		for i in range(len(rawDat)):
			im = rawDat[i]
			handleError(FCDriver.fc2RetrieveBuffer(context, byref(im)))
		
	def convertImages(self):
		'''
		Converts all the images collected by the camera based on the BGR
		pixel format.
		'''
		rawDat = self.rawImageData
		conDat = self.conImageData
		for i in range(len(rawDat)):
			handleError(FCDriver.fc2ConvertImageTo(fc2PixelFormat['BGR'], byref(rawDat[i]), byref(conDat[i])))

	def setImageSettings(self, roi):
		'''Used to set custom image sizes.'''
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
					
# ----- Triggering Functions

	def enableSoftwareTrigger(self):
		'''Enable software triggering of camera.'''
		context = self.context
		triggerMode = fc2TriggerMode()
		triggerMode.onOff = True
		triggerMode.mode = 0;
		triggerMode.parameter = 0;
		triggerMode.source = 7;
		handleError(FCDriver.fc2SetTriggerMode(context, byref(triggerMode)))
	
	def fireSoftwareTrigger(self):
		'''
		Triggers the camera when software triggering is enabled. Will wait
		until trigger is available before triggering.
		'''
		context = self.context
		while self.getRegister(0x62C):
			pass
		handleError(FCDriver.fc2FireSoftwareTrigger(context))		
	
	def enableHardwareTrigger(self):
		'''Enable hardware triggering of camera.'''
		context = self.context
		triggerMode = fc2TriggerMode()
		triggerMode.onOff = True
		triggerMode.mode = 0;
		triggerMode.parameter = 0;
		triggerMode.source = 0;
		handleError(FCDriver.fc2SetTriggerMode(context, byref(triggerMode)))
		while (self.getRegister(0x62C) & 0x001):
			pass		

# ----- Timestamp Functions
	
	def enableTimestamps(self):
		'''Turns embedded image timestamps on.'''
		self.setRegister(0x12F8, 0x00000001)
	
	def parseTimestamp(self, im):
		'''Parses the timestamp encoded in an image.'''
		def binarify(n, d):
			'''
			Outputs a string representing the binary representation of n with d digits,
			adding padding zeros on the left.
			'''
			s = bin(n)
			s = s[2:]
			while len(s) < d:
				s = '0' + s
			return s
		
		data = im.pData
		byteString = data[0:4]
		byteArray = map(ord, byteString)
		acc = ''
		for b in byteArray:
			acc += binarify(b, 8)

		secondCount = int(acc[0:7], 2)
		cycleCount = int(acc[7:20], 2)
		cycleOffset = int(acc[20:], 2)
		timestamp = Timestamp(secondCount, cycleCount, cycleOffset)
		return timestamp.decodeTime()
			
	def extractTimestamps(self):
		'''
		Extracts all of the timestamps from the images collected and stores
		them in the timestamps array.
		'''
		timestamps = self.timestamps
		for i in range(len(timestamps)):
			im = self.rawImageData[i]
			ts = self.parseTimestamp(im)
			timestamps[i] = ts
		t0 = timestamps[0]
		for i in range(len(timestamps)):
			timestamps[i] = (timestamps[i] - t0) * 1000
	
# ----- Register Manipulation Functions	

	def getRegister(self, addr):
		'''
		Gets the value of the camera register at the given address.'''
		context = self.context
		val = c_ulong()
		handleError(FCDriver.fc2ReadRegister(context, addr, byref(val)))
		return val.value
	
	def setRegister(self, addr, val):
		'''
		Sets the value of the camera register at the given address to the
		given value.
		'''
		context = self.context
		val = c_uint(val)
		handleError(FCDriver.fc2WriteRegister(context, addr, val))
		
# ----- Leftover Functions

	def setConfig(self, numOfImages):
		'''Sets the camera configuration.'''
		context = self.context
		config = fc2Config()
		config.numBuffers = numOfImages + 1
		config.numImageNotifications = 1
		config.grabTimeout = 100
		config.grabMode = fc2GrabMode['BUFFER_FRAMES']
		config.isochBusSpeed = fc2BusSpeed['SPEED_UNKNOWN']
		config.asyncBusSpeed = fc2BusSpeed['ANY']
		config.bandwidthAllocation = fc2BandwidthAllocation['ON']
		handleError(FCDriver.fc2SetConfiguration(context, byref(config)))

	def clearBuffer(self):
		'''
		Clears out image buffer. Used to ensure that images from previous
		runs are removed from camera.
		''' 
		context = self.context
		im = self.initializeImage()
		while True:
			e	= FCDriver.fc2RetrieveBuffer(context, byref(im))
			if e == 18:	# Timeout
				return
			elif e != 0:	# Other error
				handleError(e)

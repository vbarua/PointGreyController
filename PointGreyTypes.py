from ctypes import *

fc2Context = c_void_p
fc2ImageImpl = c_void_p
fc2PGRGuid = c_uint*4

MAX_STRING_LENGTH = 512


fc2ErrorCodeStrings = [
    'Function returned with no errors.',
    'General failure.',
    'Function has not been implemented.',
    'Could not connect to Bus Master.',
    'Camera has not been connected.',
    'Initialization failed.', 
    'Camera has not been initialized.',
    'Invalid parameter passed to function.',
    'Setting set to camera is invalid.',         
    'Invalid Bus Manager object.',
    'Could not allocate memory.', 
    'Low level error.',
    'Device not found.',
    'GUID failure.',
    'Packet size set to camera is invalid.',
    'Invalid mode has been passed to function.',
    'Error due to not being in Format7.',
    'This feature is unsupported.',
    'Timeout error.',
    'Bus Master Failure.',
    'Generation Count Mismatch.',
    'Look Up Table failure.',
    'IIDC failure.',
    'Strobe failure.',
    'Trigger failure.',
    'Property failure.',
    'Property is not present.',
    'Register access failed.',
    'Register read failed.',
    'Register write failed.',
    'Isochronous failure.',
    'Isochronous transfer has already been started.',
    'Isochronous transfer has not been started.',
    'Isochronous start failed.',
    'Isochronous retrieve buffer failed.',
    'Isochronous stop failed.',
    'Isochronous image synchronization failed.',
    'Isochronous bandwidth exceeded.',
    'Image conversion failed.',
    'Image library failure.',
    'Buffer is too small.',
    'There is an image consistency error.',
    'Undefined'
]

fc2PixelFormat = {
	'MONO8'	: 0x80000000, # < 8 bits of mono information. 
	'411YUV8'	: 0x40000000, # YUV 4:1:1. 
	'422YUV8'	: 0x20000000, # YUV 4:2:2. 
	'444YUV8'	: 0x10000000, # YUV 4:4:4. 
	'RGB8'		: 0x08000000, # R = G = B = 8 bits. 
	'MONO16'	: 0x04000000, # 16 bits of mono information. 
	'RGB16'	: 0x02000000, # R = G = B = 16 bits. 
	'S_MONO16'	: 0x01000000, # 16 bits of signed mono information. 
	'S_RGB16'	: 0x00800000, # R = G = B = 16 bits signed. 
	'RAW8'		: 0x00400000, # 8 bit raw data output of sensor. 
	'RAW16'	: 0x00200000, # 16 bit raw data output of sensor. 
	'MONO12'	: 0x00100000, # 12 bits of mono information. 
	'RAW12'	: 0x00080000, # 12 bit raw data output of sensor. 
	'BGR'		: 0x80000008, # 24 bit BGR. 
	'BGRU'		: 0x40000008, # 32 bit BGRU. 
	'RGB'		: 0x08000000, # 24 bit RGB. 
	'RGBU'		: 0x40000002, # 32 bit RGBU. 
	'BGR16'	: 0x02000001, # R = G = B = 16 bits. 
	'BGRU16'		: 0x02000002, # 64 bit BGRU. 
	'422YUV8_JPEG'	: 0x40000001, # JPEG compressed stream. 
	'NUM_PIXEL_FORMATS'			: 20, 	# Number of pixel formats. 
	'UNSPECIFIED_PIXEL_FORMAT'	: 0 	# Unspecified pixel format. 
}

fc2FrameRate = {
    'FRAMERATE_1_875' : 0,       
    'FRAMERATE_3_75' : 1,    
    'FRAMERATE_7_5' : 2,     
    'FRAMERATE_15' : 3,    
    'FRAMERATE_30' : 4,      
    'FRAMERATE_60' : 5,      
    'FRAMERATE_120' : 6, 
    'FRAMERATE_240' : 7, 
    'FRAMERATE_FORMAT7' : 8
}

fc2VideoMode = {
	'VIDEOMODE_160x120YUV444' : 0,
    'VIDEOMODE_320x240YUV422' : 1,
    'VIDEOMODE_640x480YUV411' : 2,
    'VIDEOMODE_640x480YUV422' : 3,
    'VIDEOMODE_640x480RGB' : 4,
    'VIDEOMODE_640x480Y8' : 5,
    'VIDEOMODE_640x480Y16' : 6,
    'VIDEOMODE_800x600YUV422' : 7,
    'VIDEOMODE_800x600RGB' : 8,
    'VIDEOMODE_800x600Y8' : 9,
    'VIDEOMODE_800x600Y16' : 10,
    'VIDEOMODE_1024x768YUV422' : 11,
    'VIDEOMODE_1024x768RGB' : 12,
    'VIDEOMODE_1024x768Y8' : 13,
    'VIDEOMODE_1024x768Y16' : 14,
    'VIDEOMODE_1280x960YUV422' : 15,
    'VIDEOMODE_1280x960RGB' : 16,
    'VIDEOMODE_1280x960Y8' : 17,
    'VIDEOMODE_1280x960Y16' : 18,
    'VIDEOMODE_1600x1200YUV422' : 19,
    'VIDEOMODE_1600x1200RGB' : 20,
    'VIDEOMODE_1600x1200Y8' : 21,
    'VIDEOMODE_1600x1200Y16' : 22,
    'VIDEOMODE_FORMAT7' : 23
}
	
fc2BayerTileFormat = {
    'NONE' : 0, # No bayer tile format. 
    'RGGB' : 1, # Red-Green-Green-Blue. 
    'GRBG' : 2, # Green-Red-Blue-Green. 
    'GBRG' : 3, # Green-Blue-Red-Green. 
    'BGGR' : 4, # Blue-Green-Green-Red. 
}

fc2ImageFileFormat = {
    'FROM_FILE_EXT' : -1, # Determine file format from file extension. 
    'PGM' : 0, # Portable gray map. 
    'PPM' : 1, # Portable pixmap. 
    'BMP' : 2, # Bitmap. 
    'JPEG' : 3, # JPEG. 
    'JPEG2000' : 4, # JPEG 2000. 
    'TIFF' : 5, # Tagged image file format. 
    'PNG' : 6, # Portable network graphics. 
    'RAW' : 7, # Raw data. 
}

fc2GrabMode = {
	'DROP_FRAMES' : 0,
    'BUFFER_FRAMES' : 1, 
    'UNSPECIFIED_GRAB_MODE' : 2
}

fc2BusSpeed = {
    'S100' : 0, # 100Mbits/sec. */
    'S200' : 1, # 200Mbits/sec. */
    'S400' : 2, # 400Mbits/sec. */
    'S480' : 3, # 480Mbits/sec. Only for USB2 cameras. */
    'S800' : 4, # 800Mbits/sec. */
    'S1600' : 5, # 1600Mbits/sec. */
    'S3200' : 6, # 3200Mbits/sec. */
    'S5000' : 7, # 5000Mbits/sec. Only for USB3 cameras. */
    '10BASE_T' : 8, # 10Base-T. Only for GigE cameras. */
    '100BASE_T' : 9, # 100Base-T.  Only for GigE cameras.*/
    '1000BASE_T' : 10, # 1000Base-T (Gigabit Ethernet).  Only for GigE cameras. */
    '10000BASE_T' : 11, # 10000Base-T.  Only for GigE cameras. */
    'S_FASTEST' : 12, # The fastest speed available. */
    'ANY' : 13, # Any speed that is available. */
    'SPEED_UNKNOWN' : -1 # Unknown bus speed. */
}

fc2BandwidthAllocation = {
	'OFF' : 0,
	'ON' : 1,
	'UNSUPPORTED' : 2,
	'UNSPECIFIED' : 3,
}

fc2VideoMode = {
    'MODE_0' : 0,
    'MODE_1' : 1,
    'MODE_2' : 2,
    'MODE_3' : 3,
    'MODE_4' : 4,
    'MODE_5' : 5,
    'MODE_6' : 6,
    'MODE_7' : 7,
    'MODE_8' : 8,
    'MODE_9' : 9,
    'MODE_10' : 10,
    'MODE_11' : 11,
    'MODE_12' : 12,
    'MODE_13' : 13,
    'MODE_14' : 14,
    'MODE_15' : 15,
    'MODE_16' : 16,
    'MODE_17' : 17,
    'MODE_18' : 18,
    'MODE_19' : 19,
    'MODE_20' : 20,
    'MODE_21' : 21,
    'MODE_22' : 22,
    'MODE_23' : 23,
    'MODE_24' : 24,
    'MODE_25' : 25,
    'MODE_26' : 26,
    'MODE_27' : 27,
    'MODE_28' : 28,
    'MODE_29' : 29,
    'MODE_30' : 30,
    'MODE_31' : 31,
}

fc2PropertyType = {
	'BRIGHTNESS' : 0,
	'AUTO_EXPOSURE' : 1,
	'SHARPNESS' : 2,
	'WHITE_BALANCE' : 3,
	'HUE' : 4,
	'SATURATION' : 5,
	'GAMMA' : 6,
	'IRIS' : 7,
	'FOCUS' : 8,
	'ZOOM' : 9,
	'PAN' : 10,
	'TILT' : 11,
	'SHUTTER' : 12,
	'GAIN' : 13,
	'TRIGGER_MODE' : 14,
	'TRIGGER_DELAY' : 15,
	'FRAME_RATE' : 16,
	'TEMPERATURE' : 17,
}

fc2Register = {
	'Initialize' : 0x000,
	'Power' : 0x610,
	'SoftwareTrigger' : 0x62C,
	'Brightness' : 0x800,
	'AutoExposure': 0x804,
	'Sharpness' : 0x808,
	'Gamma': 0x818,
	'Shutter': 0x81C,
	'Gain': 0x820,
	'TriggerMode': 0x830,
	'TriggerDelay': 0x834,
	'FrameRate': 0x83C,
	'Pan': 0x884,
	'Tilt': 0x888,
	'SoftwareTrigger': 0x62C,
	'TriggerInq': 0x530
}	

class fc2Property(Structure):
		
	_fields_ = [
				('type', c_int),
				('present', c_bool),
				('absControl', c_bool),
				('onePush', c_bool),
				('onOff', c_bool),
				('autoManualMode', c_bool),
				('valueA', c_uint),  
				('valueB', c_uint),
				('absValue', c_float),
				('reserved', c_uint*8)
				]

class fc2PropertyInfo(Structure):
	_fields_ = [
				('type', c_int),
				('present', c_bool),
				('autoSupported', c_bool),
				('manualSupported', c_bool),
				('onOffSupported', c_bool ),
				('onePushSupported', c_bool),
				('absValSupported', c_bool),
				('readOutSupported', c_bool),
				('min', c_uint),
				('max', c_uint),
				('absMin', c_float),
				('absMax', c_float),
				('pUnits', c_char * MAX_STRING_LENGTH),
				('pUnitAbbr', c_char * MAX_STRING_LENGTH),
				('reserved', c_uint*8)
				]

class fc2Format7ImageSettings(Structure):
	_fields_ = [
				('mode', c_int),
				('offsetX', c_uint),
				('offsetY', c_uint),
				('width', c_uint),
				('height', c_uint),
				('pixelFormat', c_int),
				('reserved', c_uint*8)	
	]
	
class fc2Config(Structure):
	_fields_ = [
				('numBuffers', c_uint),
				('numImageNotifications', c_uint),
				('minNumImageNotifications', c_uint),
				('grabTimeout', c_int),
				('grabMode', c_int),  
				('isochBusSpeed', c_int), 
				('asyncBusSpeed', c_int), 
				('bandwidthAllocation', c_int), 
				('registerTimeoutRetries', c_uint),
				('registerTimeout', c_uint),
				('reserved', c_uint*16)
				] 

class fc2TriggerMode(Structure):
	_fields_ = [
				('onOff', c_bool),
				('polarity', c_uint),
				('source', c_uint),
				('mode', c_uint),
				('parameter', c_uint),     
				('reserved[8]', c_uint)
				]

class fc2Version(Structure):
	_fields_ = [
				('major', c_uint),
				('minor', c_uint),
				('type', c_uint),
				('build', c_uint)
				]
				
class fc2Image(Structure):
	_fields_ = [
				('rows', c_uint),
   				('cols', c_uint),
				('stride', c_uint),
				('pData', c_char_p),
				('dataSize', c_uint),
				('receivedDataSize', c_uint),
				('format', c_uint),	#FC2PixelFormat
				('bayerFormat', c_uint),	# FC2BayerTileFormat
				('imageImpl', fc2ImageImpl)	
				]
				
class fc2Timestamp(Structure):
	_fields_ = [
	('seconds', c_longlong),
	('microSeconds', c_uint),
	('cycleSeconds', c_uint),
	('cycleCount', c_uint),
	('cycleOffset', c_uint),
	('reserved',  c_uint*8)
	]
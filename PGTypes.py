from ctypes import *

fc2Context = c_void_p
fc2ImageImpl = c_void_p
fc2PGRGuid = c_uint*4


FULL_32BIT_VALUE = 0x7FFFFFFF

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
    'Filler',
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

fc2BayerTileFormat = {
    'NONE' : 0, # No bayer tile format. 
    'RGGB' : 1, # Red-Green-Green-Blue. 
    'GRBG' : 2, # Green-Red-Blue-Green. 
    'GBRG' : 3, # Green-Blue-Red-Green. 
    'BGGR' : 4, # Blue-Green-Green-Red. 
    'FORCE_32BITS' : FULL_32BIT_VALUE
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
    'FORCE_32BITS' : FULL_32BIT_VALUE
}

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
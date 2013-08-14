from PointGreyController import ROI, PointGreyController
from time import sleep

class PointGreyBuilder(object):
	"""
	Builder for PointGreyControllers specific to the QDG Framework
	""" 
	
	def __init__(self, values):
		for (k, v) in values.items():
			setattr(self, k, v)
			
	def buildController(self):
		roi = ROI()
		if (self.useROI or self.useROICenter):
			if (self.useROICenter):
				roi.setROICenter(self.ROI_center, self.ROI_width, self.ROI_height)	
			else:
				roi.setROI(self.ROI_left, self.ROI_top, self.ROI_width, self.ROI_height)
		PGC = PointGreyController(expTime_ms = self.expTime_ms, gain = self.gain, roi = roi, boostFramerate = self.boostFramerate)								
		return PGC
		
if __name__ == "__main__":
	pointgrey_values = dict(
							gain = 0,
							expTime_ms = 0.5,
							useROI = False,			# Use Region of Interest
							useROICenter = False,	# Use Region of Interest based on center point.
							ROI_left = 100,
							ROI_top = 150,
							ROI_width = 300,
							ROI_height = 200,
							ROI_center = (430, 640),	# (x, y)
							boostFramerate = True
							)
	PGCBuilder = PointGreyBuilder(pointgrey_values)
	PGC = PGCBuilder.buildController()
	numOfImages = 4
	PGC.numOfImages = numOfImages
	PGC.enableSoftwareTrigger()
	PGC.setDataBuffers(numOfImages)
	PGC.start()
	count = 0
	while count < numOfImages:
		print "Fire Trigger: ", str(count + 1)
		PGC.fireSoftwareTrigger()
		count += 1 
	PGC.stop()
	PGC.saveLog()	
	PGC.savePNGImages()
	del PGC
	
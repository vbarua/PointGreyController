numOfImages = 5		
roi = ROI()		
roi.setROI(50, 200, 300, 600)
PGC = PointGreyController(numOfImages, 30, 0)
PGC.enableSoftwareTrigger()
print "Trigger Enabled"
PGC.start()
PGC.clearBuffer()

rawImages = [PGC.initializeImage() for _ in range(numOfImages)]
# Used to take images
print "Firing Triggers"
for i in range(numOfImages):
	# sleep(2.)
	print "Fire " + str(i)
	PGC.fireSoftwareTrigger()

conImages = [[]]*numOfImages	
	
print "Retrieving Images"	
for im in rawImages:
	PGC.retrieveImage(im)
	print PGC.parseTimestamp(im)
	

print "Converting Images"
for i in range(len(conImages)):
	conImages[i] = PGC.convertImage(rawImages[i])

print "Saving"
i = 0	
for im in conImages:
	fname = str(i) + '.png'
	i += 1
	PGC.saveImage(im, fname)

# raw1 = PGC.initializeImage()
# raw2 = PGC.initializeImage()
# raw3 = PGC.initializeImage()
# raw4 = PGC.initializeImage()
# raw5 = PGC.initializeImage()
# print "Firing Trigger"
# raw_input()
# PGC.fireSoftwareTrigger()
# raw_input()
# PGC.fireSoftwareTrigger()
# PGC.fireSoftwareTrigger()
# PGC.fireSoftwareTrigger()
# PGC.fireSoftwareTrigger()
# print "Retrieving Images"
# PGC.retrieveImage(raw1)
# print "1"
# PGC.retrieveImage(raw2)
# print "2"
# PGC.retrieveImage(raw3)
# print "3"
# PGC.retrieveImage(raw4)
# print "4"
# PGC.retrieveImage(raw5)
# print "5"
# print "Converting"
# con1 = PGC.convertImg(raw1)
# con2 = PGC.convertImg(raw2)
# con3 = PGC.convertImg(raw3)
# con4 = PGC.convertImg(raw4)
# con5 = PGC.convertImg(raw5)
# print "Saving"
# PGC.saveImage(con1, 'img1.png')
# PGC.saveImage(con2, 'img2.png')
# PGC.saveImage(con3, 'img3.png')
# PGC.saveImage(con4, 'img4.png')
# PGC.saveImage(con5, 'img5.png')	
	
PGC.stop()
import matplotlib.pyplot as plt
from PIL import Image
import os

#coordinates are in pixels from top left

framesize = (960,540)   #size of output video
n_frames = 100			 
framerate = 30   		#frames per second
filename = 'video.mp4'

sourceimage = Image.open('halpha5.jpg')
sourcelocation = [236,240]   #starting location of the source image (top left corner)
centred = False         # centres the source image, overwrites sourcelocation
source_step = [5,0]    # x,y velocity (pixels per frame)
scaling = 0.05         #scale the source image by this factor

lenses = [ [480,270,200],	#lens [x,y,einstein radius]
			[480,370,0],
			]
lens_step = [0,0]# [5,0]    # x,y velocity (pixels per frame)

def main():
	sourceimagesize = sourceimage.size
	if centred:
		#centre source image by moving top left of source to these x,y coordinates. (Measured from top left)
		sourcelocation[:] = [framesize[0]/2-(sourceimagesize[0]*scaling/2),framesize[1]/2-(sourceimagesize[1]*scaling/2)]
	print('Source image location:', sourcelocation)

	if not os.path.exists('./frames/'):
		os.makedirs('./frames/')

	sourcepixels = sourceimage.load()
	lensedimage = Image.new("RGB",framesize)
	lensedpixels = lensedimage.load()

	print('Generating', n_frames, 'frames')

	for frame in range(n_frames):		#for each frame of the movie
		for x in range(lensedimage.size[0]):
			for y in range(lensedimage.size[1]):		#loop over all pixels in the movie frame (lens plane)
				offset_total = [0,0]
				for l in lenses:
					offset = sourceoffset(x,y,l[0],l[1],l[2])
					offset_total[0] += offset[0]
					offset_total[1] += offset[1]

				source = [(x+offset_total[0]-sourcelocation[0])/scaling,(y+offset_total[1]-sourcelocation[1])/scaling]

				#read colour from source pixel, Set pixel x,y colour to source pixel colour
				if source[0] < 0 or source [0] > sourceimagesize[0]-1 or source[1] < 0 or source[1] > sourceimagesize[1]-1:
					lensedimage.putpixel((x, y), (0,0,0))
				else:
					source = int(round(source[0])), int(round(source[1]))
					lensedimage.putpixel((x, y), sourcepixels[source])
				
		lensedimage.save('./frames/frame%03d.jpeg'%(frame))
		#lensedimage.show()

		#move each lens for the next frame
		for l in lenses:
			l[0] += lens_step[0]
			l[1] += lens_step[1]
		sourcelocation[0] += source_step[0]
		sourcelocation[1] += source_step[1]
		print(frame)

	os.system('./ffmpeg-2 -y -f image2 -r {} -i ./frames/frame%03d.jpeg -vcodec libx264 -pix_fmt yuv420p -r {} {}'.format(framerate,framerate,filename))

def sourceoffset(imagex,imagey,lensx,lensy,thetaE):
	#takes the lens postion and an x,y point on the lens plane, gives deviation on the source plane
	image = [imagex,imagey]
	lens = [lensx, lensy]
	theta = ((image[0]-lens[0])**2 + (image[1]-lens[1])**2)**0.5
	if theta == 0:
		theta=0.01
		image[0]=image[0]+0.01
		image[1]=image[1]+0.01
	beta = (theta**2 - thetaE**2)/theta
	source = beta/theta*(image[0]-lens[0])+ lens[0] -image[0], beta/theta*(image[1]-lens[1])+ lens[1]-image[1]
	#lens x,y plus sourceoffset =  coordinates on source plane
	return source

main()
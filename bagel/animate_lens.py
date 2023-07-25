# import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from photutils.centroids import centroid_com

#coordinates are in pixels from top left

s=1
HD = False 
if HD:
	s=2
framesize = (600*s,600*s)   #size of output video
n_frames = 1			 
framerate = 30   		#frames per second
filename = 'lensing_demonstration_'

sourceimage = Image.open('roll1.jpg')
sourcelocation = [300*s,300*s]   #starting location of the source image (centre)
centred = False         # centres the source image, overwrites sourcelocation (use if source is static background)
source_step = [5*s,0*s]    # x,y velocity (pixels per frame)
source_scaling = 0.8*s         #scale the source image by this factor

lenses = [ [300*s,300*s,200*s],	#lens [x, y, einsteinradius]
			] #[480,370,0],
			#]
lens_step = [0*s,0*s]# [5,0]    # x,y velocity (pixels per frame)

# lensimage = Image.open('black_hole_2.png')
lens_scaling = 0.05*s 

show_lens = False
markers = False 
labels = False
fadepoint = 60
show_plots = False

magplot_location = [100*s,510*s] #lower left
magplot_size = [200*s,100*s]
max_brightness = 4.2
min_brightness = 0.4
cenplot_location = [730*s,510*s]
max_centroid = 240*s
min_centroid = 247*s
#--------------------------------------------------------------------------------------------


if labels:
	filename += 'l'
if markers:
	filename += 'm'
if show_plots:
	filename += 'p'	
if HD:
	filename += 'HD'
filename += '.mp4'

def main():
	sourceimagesize = sourceimage.size
	# lensimage_r = lensimage.resize((int(round(lensimage.size[0]*lens_scaling)),int(round(lensimage.size[1]*lens_scaling))))
	# lensimage_size = lensimage_r.size

	if centred:
		#centre source image by moving top left of source to these x,y coordinates. (Measured from top left)
		sourcelocation[:] = [framesize[0]/2,framesize[1]/2]
	print('Source image location:', sourcelocation)
	print('Filename:', filename)

	if labels:
		font = ImageFont.truetype('Arial', 16*s)

	if not os.path.exists('./frames/'):
		os.makedirs('./frames/')

	sourcepixels = sourceimage.load()
	lensedimage = Image.new("RGBA",framesize)
	lensedpixels = lensedimage.load()

	print('Generating', n_frames, 'frames')

	if show_plots:
		magplot_brightness = np.zeros(n_frames)
		magplot_position = np.zeros([n_frames,2])
		# magplot_centroid = np.zeros([n_frames,2])
		centplot_pos = np.zeros([n_frames,2])

	for frame in range(n_frames):		#for each frame of the movie
		for x in range(lensedimage.size[0]):
			for y in range(lensedimage.size[1]):		#loop over all pixels in the movie frame (lens plane)
				offset_total = [0,0]
				for l in lenses:
					offset = sourceoffset(x,y,l[0],l[1],l[2])
					offset_total[0] += offset[0]
					offset_total[1] += offset[1]

				source = [(x+offset_total[0]-sourcelocation[0]+sourceimagesize[0]*source_scaling/2)/source_scaling,
							(y+offset_total[1]-sourcelocation[1]+sourceimagesize[1]*source_scaling/2)/source_scaling]

				#read colour from source pixel, Set pixel x,y colour to source pixel colour
				if source[0] < 0 or source [0] > sourceimagesize[0]-1 or source[1] < 0 or source[1] > sourceimagesize[1]-1:
					# lensedimage.putpixel((x, y), (0,0,0))
					lensedimage.putpixel((x, y), (255,255,255))
					pass
				else:
					source = int(round(source[0])), int(round(source[1]))
					lensedimage.putpixel((x, y), sourcepixels[source])

				
		
		# lensimage_location = (int(round(lenses[0][0]-lensimage_size[0]/2)) , int(round(lenses[0][1]-lensimage_size[1]/2)))


		draw = ImageDraw.Draw(lensedimage)

		# dot_rad = 10
		# draw.ellipse([(lenses[0][0]-lenses[0][2],lenses[0][1]-lenses[0][2]),(lenses[0][0]+lenses[0][2],lenses[0][1]+lenses[0][2])], fill=None, outline='black', width=2)
		# draw.ellipse([(lenses[0][0]-dot_rad,lenses[0][1]-dot_rad),(lenses[0][0]+dot_rad,lenses[0][1]+dot_rad)], fill='black', outline='black', width=2)

		if show_plots or markers:
			image_array = np.array(lensedimage)
			flat_array = np.mean(image_array,axis=2)
			brightness = np.mean(image_array)
			centroid = centroid_com(flat_array)


		if show_plots:
			if frame > fadepoint:
				opacity = min(255,(frame-fadepoint)*10)
			else:
				opacity = 0
			# opacity = 255
			new_mag_point = [magplot_location[0] + frame*magplot_size[0]/n_frames , magplot_location[1] - brightness*magplot_size[0]/(max_brightness-min_brightness) ]
			magplot_position[frame,:] = new_mag_point
			magplot_brightness[frame] = brightness
			for i, bright in enumerate(magplot_brightness[:frame]):
				x = magplot_position[i,0]
				y = magplot_position[i,1]
				draw.ellipse([x-1*s,y-1*s,x+1*s,y+1*s],fill=(opacity,opacity,opacity,225))
			draw.line([magplot_location[0]-5*s,magplot_location[1]-5*s,magplot_location[0]-5*s,magplot_location[1]-magplot_size[1]],fill=(opacity,opacity,opacity,225))
			draw.line([magplot_location[0]-5*s,magplot_location[1]-5*s,magplot_location[0]+magplot_size[0],magplot_location[1]-5*s],fill=(opacity,opacity,opacity,225))
			draw.text((magplot_location[0]-10*s,magplot_location[1]-magplot_size[1]/2),'Brightness',fill=(opacity,opacity,opacity,255),font=font,anchor='rm')
			# draw.text((magplot_location[0]+magplot_size[0]/2,magplot_location[1]+5),'Time',fill=(opacity,opacity,opacity,255),font=font,anchor='mt')
			
			# centroid = centroid_com(np.flip(flat_array,axis=0))
			new_cent_point = [cenplot_location[0] + centroid[0]/framesize[0]*magplot_size[0] , (cenplot_location[1]-magplot_size[1]/2) - (centroid[1]- min_centroid)/(max_centroid-min_centroid)*30*s ]
			centplot_pos[frame,:] = new_cent_point
			# magplot_centroid[frame] = brightness
			for i, bright in enumerate(magplot_brightness[:frame]):
				x = centplot_pos[i,0]
				y = centplot_pos[i,1]
				draw.ellipse([x-1*s,y-1*s,x+1*s,y+1*s],fill=(opacity,opacity,opacity,225))
			draw.line([cenplot_location[0]-5*s,cenplot_location[1]-5*s,cenplot_location[0]-5*s,cenplot_location[1]-magplot_size[1]],fill=(opacity,opacity,opacity,225))
			draw.line([cenplot_location[0]-5*s,cenplot_location[1]-5*s,cenplot_location[0]+magplot_size[0],cenplot_location[1]-5*s],fill=(opacity,opacity,opacity,225))
			draw.multiline_text((cenplot_location[0]-10*s,cenplot_location[1]-magplot_size[1]/2),'Apparent\nPosition',fill=(opacity,opacity,opacity,255),font=font,anchor='rm')
			# draw.text((cenplot_location[0]+magplot_size[0]/2,cenplot_location[1]+5),'Time',fill=(opacity,opacity,opacity,255),font=font,anchor='mt')

			# print(brightness,centroid[0],centroid[1])			


		if show_lens:
			lensedimage.paste(lensimage_r,lensimage_location)

		if markers:
			draw.line((lenses[0][0]+2*s,lenses[0][1],lenses[0][0]-2*s,lenses[0][1]),fill=(255,0,0,255))
			draw.line((lenses[0][0],lenses[0][1]+2*s,lenses[0][0],lenses[0][1]-2*s),fill=(255,0,0,255))
			draw.line((sourcelocation[0]+2*s,sourcelocation[1],sourcelocation[0]-2*s,sourcelocation[1]),fill=(0,255,0,255))
			draw.line((sourcelocation[0],sourcelocation[1]+2*s,sourcelocation[0],sourcelocation[1]-2*s),fill=(0,255,0,255))
			draw.line((centroid[0]+2*s,centroid[1],centroid[0]-2*s,centroid[1]),fill=(0,128,255,255))
			draw.line((centroid[0],centroid[1]+2*s,centroid[0],centroid[1]-2*s),fill=(0,128,255,255))


		if labels:
			if frame > fadepoint:
				opacity = max(0,255+fadepoint*10-frame*10)
			else:
				opacity = 255
			draw.text((lenses[0][0],lenses[0][1]+60*s),'Black Hole',fill=(opacity,opacity,opacity,255),anchor='mm',font=font)
			draw.text((20*s,190*s),'Background Star',fill=(opacity,opacity,opacity,255),font=font)
			# draw.line((lenses[0][0]-20,lenses[0][1]+50),fill=(255,255,255,128))


		# draw.text((5*s,537*s),'UC Berkeley/Moving Universe Lab',fill=(128,128,128,255),font=ImageFont.truetype('Arial', 14*s),anchor='lb')



		# lensedimage.save('./frames/frame%03d.jpeg'%(frame))
		lensedimage.save('./frames/frame%03d.png'%(frame))
		#lensedimage.show()

		#move each lens for the next frame
		for l in lenses:
			l[0] += lens_step[0]
			l[1] += lens_step[1]
		sourcelocation[0] += source_step[0]
		sourcelocation[1] += source_step[1]
		print(frame)
	

	# os.system('./ffmpeg-2 -y -f image2 -r {} -i ./frames/frame%03d.jpeg -vcodec libx264 -pix_fmt yuv420p -r {} {}'.format(framerate,framerate,filename))

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


# main()
# markers = True
# filename = 'lensing_demonstration_marked.mp4'
main()


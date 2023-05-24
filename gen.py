from PIL import Image,ImageDraw,ImageFont

EPD_WIDTH       = 168
EPD_HEIGHT      = 400

BLACK  = 0x000000   #   00  BGR
WHITE  = 0xffffff   #   01
YELLOW = 0x00ffff   #   10
RED    = 0x0000ff   #   11

def getbuffer(image):
	# Create a pallette with the 4 colors supported by the panel
	pal_image = Image.new("P", (1,1))
	pal_image.putpalette( (0,0,0,  255,255,255,  255,255,0,   255,0,0) + (0,0,0)*252)

	# Check if we need to rotate the image
	imwidth, imheight = image.size
	if(imwidth == EPD_WIDTH  and imheight == EPD_HEIGHT):
		image_temp = image
	elif(imwidth == EPD_HEIGHT and imheight == EPD_WIDTH ):
		image_temp = image.rotate(90, expand=True)
	#else:
		#logger.warning("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, EPD_WIDTH , EPD_HEIGHT))

	# Convert the soruce image to the 4 colors, dithering if needed
	image_4color = image_temp.convert("RGB").quantize(palette=pal_image)
	buf_4color = bytearray(image_4color.tobytes('raw'))

	# into a single byte to transfer to the panel
	buf = [0x00] * int(EPD_WIDTH  * EPD_HEIGHT / 4)
	idx = 0
	for i in range(0, len(buf_4color), 4):
		buf[idx] = str((buf_4color[i] << 6) + (buf_4color[i+1] << 4) + (buf_4color[i+2] << 2) + buf_4color[i+3]) + ","
		idx += 1

	return buf

img = Image.new('RGB', (EPD_WIDTH, EPD_HEIGHT), 0xffffff)  
draw = ImageDraw.Draw(img)
draw.text((5, 0), 'hello world', fill = RED)
draw.line((5, 170, 80, 245), fill = RED)
draw.rectangle((5, 170, 80, 245), outline = BLACK)
draw.arc((5, 250, 80, 325), 0, 360, fill = BLACK)
draw.chord((90, 250, 165, 325), 0, 360, fill = RED)
buf = getbuffer(img)
print(len(buf))
with open('d.txt','w') as f:
	f.writelines((buf))

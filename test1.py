import PIL
from PIL import Image
import numpy
from dxfwrite import DXFEngine as dxf

filepath = 'test.jpg'
width_mm = 3000
height_mm = 2000
screw_mm = 8
hole_diam_mm = 2

w = int(width_mm / screw_mm)
h = int(height_mm / screw_mm)
offset_w = round((width_mm - w * screw_mm) / 2 + screw_mm / 2, 2)
offset_h = round((height_mm - h * screw_mm) / 2 + screw_mm / 2, 2)

print(w, h, offset_w, offset_h)
threshold = 200

img = Image.open(filepath).convert('L')
img = img.resize((w, h), PIL.Image.ANTIALIAS)
(width, height) = img.size
greyscaleMap = list(img.getdata())
greyscaleMap = numpy.array(greyscaleMap)
greyscaleMap = greyscaleMap.reshape((height, width))

print(greyscaleMap)
print(len(greyscaleMap), len(greyscaleMap[0]))
print(numpy.amin(greyscaleMap))

for i in range(len(greyscaleMap)):
    for j in range(len(greyscaleMap[i])):
        if greyscaleMap[i][j] < threshold:
            greyscaleMap[i][j] = 0
        else:
            greyscaleMap[i][j] = 255

print(greyscaleMap)
print(numpy.amax(greyscaleMap))

img1 = Image.fromarray(numpy.uint8(greyscaleMap), 'L')
img1.show()
img1.save('bbb.jpg')

drawing = dxf.drawing('test.dxf')
drawing.add(dxf.line((0, 0), (0, -height_mm)))
drawing.add(dxf.line((0, 0), (width_mm, 0)))
drawing.add(dxf.line((width_mm, -height_mm), (0, -height_mm)))
drawing.add(dxf.line((width_mm, -height_mm), (width_mm, 0)))

for i in range(len(greyscaleMap)):
    for j in range(len(greyscaleMap[i])):
        if not greyscaleMap[i][j]:
            drawing.add(dxf.circle(hole_diam_mm/2, (screw_mm*j + offset_w, -screw_mm*i+ offset_h)))

drawing.save()
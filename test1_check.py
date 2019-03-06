import PIL
from PIL import Image
import numpy
from dxfwrite import DXFEngine as dxf

filepath = 'galstuk_off_4.bmp'
width_mm = 890
height_mm = 890
screw_mm = 8.7
hole_diam_mm = 2

w = int(width_mm / screw_mm)
h = int(height_mm / screw_mm)
w_ch = w * 20
h_ch = h * 20
offset_w = round((width_mm - w * screw_mm) / 2 + screw_mm / 2, 2)
offset_h = round((height_mm - h * screw_mm) / 2 + screw_mm / 2, 2)

print(w, h, offset_w, offset_h, w_ch, h_ch)
threshold = 200

img = Image.open(filepath).convert('L')
#img = img.resize((w, h), PIL.Image.ANTIALIAS)
img = img.resize((w_ch, h_ch), PIL.Image.BILINEAR)
(width, height) = img.size

img.save('big_img.jpg')
greyscaleMap = list(img.getdata())
greyscaleMap = numpy.array(greyscaleMap)
greyscaleMap = greyscaleMap.reshape((height, width))

print(greyscaleMap)
print(len(greyscaleMap), len(greyscaleMap[0]))
print(numpy.amin(greyscaleMap))
new_array = []
for i in range(0, len(greyscaleMap), 10):
    arr = []
    if (i / 10) % 2 == 1:
        for j in range(18, len(greyscaleMap[i]), 36):
            arr.append(greyscaleMap[i][j])
    else:
        for j in range(0, len(greyscaleMap[i]), 36):
            arr.append(greyscaleMap[i][j])
    new_array.append(arr)

print(new_array)
print(len(new_array), len(new_array[0]), len(new_array[1]))

for i in range(len(new_array)):
    for j in range(len(new_array[i])):
        if new_array[i][j] < threshold:
            new_array[i][j] = 0
        else:
            new_array[i][j] = 255

img1 = Image.fromarray(numpy.uint8(greyscaleMap), 'L')
img1.show()
#img1.save('bbb.jpg')

drawing = dxf.drawing(filepath + '.dxf')
#drawing.add(dxf.line((0, 0), (0, -height_mm)))
#drawing.add(dxf.line((0, 0), (width_mm, 0)))
#drawing.add(dxf.line((width_mm, -height_mm), (0, -height_mm)))
#drawing.add(dxf.line((width_mm, -height_mm), (width_mm, 0)))

for i in range(len(new_array)):
    if i % 2 == 0:
        for j in range(len(new_array[i])):
            if not new_array[i][j]:
                drawing.add(dxf.circle(hole_diam_mm/2, (screw_mm / 2 * 3.6 * j + offset_w,
                                                        (-screw_mm / 2 ) * i + offset_h)))
    else:
        for j in range(len(new_array[i])):
            if not new_array[i][j]:
                drawing.add(dxf.circle(hole_diam_mm/2, (screw_mm / 2 * 3.6 * j + offset_w + 1.8 * screw_mm / 2,
                                                        (-screw_mm / 2 ) * i + offset_h)))

# for i in range(len(greyscaleMap)):
#     for j in range(len(greyscaleMap[i])):
#         if not greyscaleMap[i][j]:
#             drawing.add(dxf.circle(hole_diam_mm/2, (screw_mm*j + offset_w, -screw_mm*i+ offset_h)))

# for i in range(0, len(greyscaleMap, 20)):
#     for j in range(0, len(greyscaleMap[i], 18)):
#         if not greyscaleMap[i][j]:
#
drawing.save()
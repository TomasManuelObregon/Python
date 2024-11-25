import numpy as np
import math
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.measure import label, regionprops
# from skimage.transform import rotate
from scipy.ndimage import rotate
plt.ion()
plt.close('all')


im = imread("imagen_m1.png")

plt.figure()
plt.imshow(im)
plt.colorbar()

imb = im>100


plt.figure()
plt.imshow(label(imb))

blobc = label(imb)==2
blobc = imb


plt.figure()
plt.imshow(blobc)

regions = regionprops(blobc.astype(np.uint8))

plt.close('all')

fig, ax = plt.subplots()
ax.imshow(blobc, cmap=plt.cm.gray)

for props in regions:
    y0, x0 = props.centroid
    orientation = props.orientation
    x1 = x0 + math.cos(orientation) * 0.5 * props.axis_minor_length
    y1 = y0 - math.sin(orientation) * 0.5 * props.axis_minor_length
    x2 = x0 - math.sin(orientation) * 0.5 * props.axis_major_length
    y2 = y0 - math.cos(orientation) * 0.5 * props.axis_major_length

    ax.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
    ax.plot((x0, x2), (y0, y2), '-r', linewidth=2.5)
    ax.plot(x0, y0, '.g', markersize=15)

    minr, minc, maxr, maxc = props.bbox
    bx = (minc, maxc, maxc, minc, minc)
    by = (minr, minr, maxr, maxr, minr)
    ax.plot(bx, by, '-b', linewidth=2.5)



unrotado = rotate(im, -orientation)

plt.figure()
plt.imshow(unrotado)

unrotado = unrotado[:,1271:1294]

plt.figure()
plt.imshow(unrotado)

plt.close('all')

plt.figure()
plt.plot(unrotado)

unrotado = unrotado - np.mean(unrotado)

plt.figure()
plt.imshow(np.fft.fftshift(np.log(np.abs(np.fft.fft2(unrotado)))))
plt.gca().set_aspect('auto')
plt.colorbar()

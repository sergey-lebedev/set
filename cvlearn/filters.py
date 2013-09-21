import cv
import cv2
import math
import time
import bisect
from plot import *
import numpy as np
images_dir = './samples'
#filename = 'DSC03539_mini.JPG'
filename = 'DSC03537_mini.JPG'
#filename = 'output_rgb.png'
fullname = '/'.join((images_dir, filename))
image = cv2.imread(fullname)

def achromatic_mask(image):
    copy = image.copy()
    (cols, rows) = cv.GetSize(cv.fromarray(copy))
    hls = cv2.cvtColor(copy, cv2.COLOR_BGR2HLS)
    (hue, lightness, saturation) = cv2.split(hls)
    inverted_mask = cv2.inRange(hue, np.array(0), np.array(0))
    #print sum(sum(inverted_mask)) / 255
    mask = cv2.bitwise_not(inverted_mask)
    cv.Set(cv.fromarray(copy), (0, 0, 0), cv.fromarray(inverted_mask))
    cv2.imshow('achromatic mask', copy)
    return mask, inverted_mask

def median_filter(image):
    #copy = image.copy()
    copy = cv2.medianBlur(image, 13)
    return copy

def simplest_color_balance(image, s1=0, s2=0, mask=None):
    #tick = time.time()
    UMAX = 255
    copy = image.copy()
    layers = cv2.split(copy)
    for i, layer in enumerate(layers):
        hist = cv2.calcHist([layer], [0], mask, [UMAX + 1], [0, UMAX])
        cumsum = hist.cumsum()
        size = cumsum[-1]
        lb = size * s1 / 100.0
        ub = size * (1 - s2 / 100.0)
        # reinit borders
        left = bisect.bisect_left(cumsum, lb)
        right = bisect.bisect_right(cumsum, ub)
        if (right - left) <= 0:
            left = UMAX / 2 - 1
            right = UMAX / 2
        #print left, right
        # replacing values
        if left != 0:
            left_mask = cv2.inRange(layer, np.array(0), np.array(left))
            cv.Set(cv.fromarray(layer), left, cv.fromarray(left_mask))
        if right != UMAX:
            right_mask = cv2.inRange(layer, np.array(right), np.array(UMAX))
            cv.Set(cv.fromarray(layer), right, cv.fromarray(right_mask))
        layers[i] = layer
    layers = map(lambda x: cv2.normalize(x, x, 0, UMAX, cv2.NORM_MINMAX), layers)
    copy = cv2.merge(layers)
    #cv2.imshow('filter', copy)
    #tock = time.time()
    #print tock - tick
    return copy

def balance(image, ax, bx, ay, by, az, bz):
    UMAX = 255
    copy = image.copy()
    copy = cv2.cvtColor(copy, cv2.COLOR_RGB2XYZ)
    layers = cv2.split(copy)
    params = np.array([ax, bx, ay, by, az, bz])
    params = params.reshape(3, 2)
    for i, layer in enumerate(layers):
        kernel = params[i][0]
        layer += params[i][1]
        layer *= kernel
        layers[i] = layer
    copy = cv2.merge(layers)
    return copy

def chromatic_adaptation(image):
    return simplest_color_balance(image, 1.5, 1.5)

def execute_chromatic_adaptation(image):
    cv2.imshow('image', image)
    if DEBUG: plot_hist(image, image_name='before', hist_type='')
    result = chromatic_adaptation(image)
    if DEBUG: plot_hist(result, image_name='after', hist_type='')
    cv2.imshow('result', result)
    #cv2.imwrite('result.bmp', result)
    (mask, inverted_mask) = achromatic_mask(result)

def execute_fft(image):
    cv2.imshow('image', image)
    # gettin layers dft
    dfts = []
    channels = cv2.split(image)
    for channel in channels:
        #cv2.imshow('channel %d'%i, channel)
        channel = np.array(channel, dtype='float')
        dft = cv2.dft(channel, flags=cv2.DFT_SCALE)
        dfts.append(dft)
    new_channels = []
    for dft in dfts:
        channel = cv2.idft(dft)
        channel = np.array(channel, dtype='uint8')
        #cv2.imshow('new channel %d'%i, channel)
        new_channels.append(channel)
    result = cv2.merge(new_channels)
    cv2.imshow('result', result)

def gaussian(d_x, sx, d_y, sy):
    x_gaussian_kernel = np.matrix(cv2.getGaussianKernel(d_x, sx))
    #print x_gaussian_kernel
    y_gaussian_kernel = np.matrix(cv2.getGaussianKernel(d_y, sy))
    #print y_gaussian_kernel
    gaussian_kernel = y_gaussian_kernel * x_gaussian_kernel.T
    #print gaussian_kernel
    #k = gaussian_kernel.sum()
    #print k
    return gaussian_kernel

def gaussian_blur(image, radius, sigma=1.0):
    gaussian_kernel = gaussian(radius, sigma, radius, sigma)
    result = cv2_convolution(image, gaussian_kernel)
    return result

def cv_convolution(image, b):
    #cv.ShowImage('image', cv.fromarray(image))
    dft_m = cv.GetOptimalDFTSize(image.shape[0] + b.shape[0] - 1)
    dft_n = cv.GetOptimalDFTSize(image.shape[1] + b.shape[1] - 1)
    print dft_m, dft_n
    #
    c = cv.CreateMat(image.shape[0] + d - 1, image.shape[1] + d - 1, cv.CV_8U)
    # getting gaussian dft
    dft_b = cv.CreateMat(dft_m, dft_n, cv.CV_64F)
    #
    tmp = cv.GetSubRect(dft_b, (0, 0, b.shape[1], b.shape[0]))
    cv.Copy(cv.fromarray(b), tmp)
    tmp = cv.GetSubRect(dft_b, (b.shape[1], 0, dft_b.cols - b.shape[1], b.shape[0]))
    cv.Zero(tmp)
    #
    cv.DFT(dft_b, dft_b, cv.CV_DXT_FORWARD, b.shape[0])
    # getting layers dft
    dfts = []
    new_channels = []
    channels = cv2.split(image)
    for i, channel in enumerate(channels):
        #cv2.imshow('channel %d'%i, channel)
        a = np.array(channel, dtype='float')
        dft_a = cv.CreateMat(dft_m, dft_n, cv.CV_64F)
        #
        tmp = cv.GetSubRect(dft_a, (0, 0, a.shape[1], a.shape[0]))
        cv.Copy(cv.fromarray(a), tmp)
        tmp = cv.GetSubRect(dft_a, (a.shape[1], 0, dft_a.cols - a.shape[1], a.shape[0]))
        cv.Zero(tmp)
        #
        cv.DFT(dft_a, dft_a, cv.CV_DXT_FORWARD, a.shape[0])
        cv.MulSpectrums(dft_a, dft_b, dft_a, 0)
        cv.DFT(dft_a, dft_a, cv.CV_DXT_INV_SCALE, c.rows)
        tmp = cv.GetSubRect(dft_a, (0, 0, c.cols, c.rows))
        #cv.Copy(tmp, c)
        channel = np.array(tmp, dtype='uint8')
        cv.ShowImage('new channel %d'%i, cv.fromarray(channel))
        new_channels.append(channel)
    result = cv2.merge(new_channels)
    return result
    #cv.ShowImage('result', cv.fromarray(result))

def cv2_convolution(image, b):
    dft_m = cv2.getOptimalDFTSize(image.shape[0] + b.shape[0] - 1)
    dft_n = cv2.getOptimalDFTSize(image.shape[1] + b.shape[1] - 1)
    d = b.shape[0]
    c = np.zeros((image.shape[0] + d - 1, image.shape[1] + d - 1), dtype='uint8')
    # getting gaussian dft
    dft_b = np.zeros((dft_m, dft_n), dtype='float64')
    dft_b[:b.shape[0], :b.shape[1]] = b
    dft_b = cv2.dft(dft_b, flags=cv2.DFT_REAL_OUTPUT)
    # getting layers dft
    dfts = []
    new_channels = []
    channels = cv2.split(image)
    for i, channel in enumerate(channels):
        #cv2.imshow('channel %d'%i, channel)
        a = np.array(channel, dtype='float64')
        dft_a = np.zeros((dft_m, dft_n), dtype='float64')
        dft_a[:a.shape[0], :a.shape[1]] = a
        dft_a = cv2.dft(dft_a, flags=cv2.DFT_REAL_OUTPUT)
        dft_a = cv2.mulSpectrums(dft_a, dft_b, 0)
        dft_a = cv2.idft(dft_a, flags= cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        tmp = dft_a[d/2:a.shape[0] + d/2, d/2:a.shape[1] + d/2]
        channel = np.array(tmp, dtype='uint8')
        #cv2.imshow('new channel %d'%i, channel)
        new_channels.append(channel)
    result = cv2.merge(new_channels)
    return result

def cv2_deconvolution(image, b):
    dft_m = cv2.getOptimalDFTSize(image.shape[0] + b.shape[0] - 1)
    dft_n = cv2.getOptimalDFTSize(image.shape[1] + b.shape[1] - 1)
    c = np.zeros((image.shape[0] + d - 1, image.shape[1] + d - 1), dtype='uint8')
    # getting gaussian dft
    dft_b = np.zeros((dft_m, dft_n), dtype='float64')
    dft_b[:b.shape[0], :b.shape[1]] = b
    psf = cv2.dft(dft_b, flags=cv2.DFT_COMPLEX_OUTPUT)
    psf2 = (psf**2).sum(-1)
    ipsf = psf / (psf2 + 0.7)[..., np.newaxis]
    # getting layers dft
    dfts = []
    new_channels = []
    channels = cv2.split(image)
    for i, channel in enumerate(channels):
        #cv2.imshow('channel %d'%i, channel)
        a = np.array(channel, dtype='float64')
        dft_a = np.zeros((dft_m, dft_n), dtype='float64')
        dft_a[:a.shape[0], :a.shape[1]] = a
        print 'deconv'
        dft_a = cv2.dft(dft_a, flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_a = cv2.mulSpectrums(dft_a, ipsf, 0)
        print dft_a
        dft_a = cv2.idft(dft_a, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        print dft_a
        tmp = dft_a[d/2:a.shape[0] + d/2, d/2:a.shape[1] + d/2]
        channel = np.array(tmp, dtype='uint8')
        cv2.imshow('new channel %d'%i, channel)
        new_channels.append(channel)
    result = cv2.merge(new_channels)
    return result

if __name__ == '__main__':
    while True:
        #execute_chromatic_adaptation(image)
        d = 15
        b = gaussian(d, d)
        cv2.imshow('image', image)
        tick = time.time()
        #result = cv_convolution(image, b)
        result = cv2_convolution(image, b)
        cv2.imwrite('blured.png', result)
        cv2.imshow('conv', result)
        result = cv2_deconvolution(result, b)
        tock = time.time()
        print tock - tick
        cv2.imshow('result', result)
        key = cv2.waitKey(10)
        if key == 27:
            break

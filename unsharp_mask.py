import cv
import cv2
import time
import filters
import numpy as np

def blend(src1, src2, mask):
    inverted_mask = cv2.bitwise_not(mask)
    layers = cv2.split(src1)
    for i, layer in enumerate(layers):
        layer = np.array(layer, dtype='float')
        layers[i] = np.array(layer*inverted_mask / 255.0, dtype='uint8')
    src1 = cv2.merge(layers)
    layers = cv2.split(src2)
    for i, layer in enumerate(layers):
        layer = np.array(layer, dtype='float')
        layers[i] = np.array(layer*mask / 255.0, dtype='uint8')
    src2 = cv2.merge(layers)
    result = cv2.add(src1, src2)
    return result

def unsharp_mask(image, amount, radius, threshold):
    sigma = 0.15
    copy = image.copy()
    cv2.imshow('copy', copy)
    converted = cv2.cvtColor(copy, cv2.COLOR_RGB2GRAY)
    blurred = filters.gaussian_blur(converted, 2*radius + 1, sigma)
    cv2.imshow('blurred', blurred)
    #blurred = cv2.blur(converted, tuple([2*radius + 1]*2))
    mask = cv2.absdiff(blurred, converted)
    mask = np.array(mask * (255.0 / mask.max()), dtype='uint8')
    (dummy, mask) = cv2.threshold(mask, threshold, 255, cv2.THRESH_TOZERO)
    cv2.imshow('mask', mask)
    corrected = filters.simplest_color_balance(copy, 15, 15, mask)
    #corrected = image.copy() * 0
    print corrected
    #cv2.imshow('corrected', corrected)
    result = blend(copy, corrected, mask)
    #result = cv2.resize(image, (width, height))
    return result

def jp_unsharp_mask(image, amount, radius, threshold):
    sigma = 0.5
    copy = image.copy()
    cv2.imshow('copy', copy)
    f = cv2.cvtColor(copy, cv2.COLOR_RGB2LAB)
    fg1 = filters.gaussian_blur(f, 2*radius + 1, sigma)
    fg2 = filters.gaussian_blur(fg1, 2*radius + 1, sigma)
    (fg1_l, dummy, dummy) = cv2.split(fg1)
    cv2.imshow('fg1_l', fg1_l)
    (fg2_l, dummy, dummy) = cv2.split(fg2)
    cv2.imshow('fg2_l', fg2_l)
    mask = cv2.absdiff(fg1_l, fg2_l)
    print 255.0 / mask.max()
    mask = np.array(mask * (255.0 / mask.max()), dtype='uint8')
    #mask = np.array(mask * 7, dtype='uint8')
    (dummy, mask) = cv2.threshold(mask, threshold, 255, cv2.THRESH_TOZERO)
    cv2.imshow('mask', mask)
    print mask
    mask = cv2.merge((mask, mask * 0, mask * 0))
    g = cv2.add(f, mask)
    result = cv2.cvtColor(g, cv2.COLOR_LAB2RGB)
    return result

def hls_unsharp_mask(image, amount, radius, threshold):
    sigma = 0.2
    copy = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
    (h, l, s) = cv2.split(copy)
    blurred = filters.gaussian_blur(l, 2*radius + 1, sigma)
    mask = cv2.absdiff(blurred, l)
    print 255.0 / mask.max()
    mask = np.array(mask * (255.0 / mask.max()), dtype='uint8')
    (dummy, mask) = cv2.threshold(mask, threshold, 255, cv2.THRESH_TOZERO)
    cv2.imshow('mask', mask)
    cv2.imshow('l before', l)
    corrected = filters.simplest_color_balance(l, 10, 10)
    #corrected = l * (1 + amount) - blurred * amount 
    cv2.imshow('corrected', corrected)
    l = blend(l, corrected, mask)
    cv2.imshow('l after', l)
    copy = cv2.merge((h, l, s))
    result = cv2.cvtColor(copy, cv2.COLOR_HLS2RGB)
    return result

def bisect_unsharp_mask(image, amount, radius, threshold):
    sigma = 0.5
    copy = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
    (h, l, s) = cv2.split(copy)
    blurred = filters.gaussian_blur(l, 2*radius + 1, sigma)
    positive_mask = cv2.addWeighted(l, 1, blurred, -1, 0)
    positive_mask = np.array(positive_mask * (255.0 / positive_mask.max()), dtype='uint8')
    negative_mask = cv2.addWeighted(l, -1, blurred, 1, 0)
    negative_mask = np.array(negative_mask * (255.0 / negative_mask.max()), dtype='uint8')
    cv2.imshow('positive_mask', positive_mask)
    cv2.imshow('negative_mask', negative_mask)
    cv2.imshow('l before', l)
    positive = l * (1 + amount)
    #cv2.imshow('positive', positive)
    l = blend(l, positive, positive_mask)
    negative = l * (1 - amount)
    l = blend(l, negative, negative_mask)
    #cv2.imshow('negative', negative)
    cv2.imshow('l after', l)
    copy = cv2.merge((h, l, s))
    result = cv2.cvtColor(copy, cv2.COLOR_HLS2RGB)
    return result

if __name__ == '__main__':
    images_dir = './samples'
    filename = 'output_rgb.png'
    #filename = 'usm_text-orig.png'
    fullname = '/'.join((images_dir, filename))
    image = cv2.imread(fullname)
    while True:
        key = cv2.waitKey(10)
        cv2.imshow('image', image)
        tick = time.time()
        #result = jp_unsharp_mask(image, 0, 1, 0)
        #result = unsharp_mask(image, 0, 3, 0)
        #result = hls_unsharp_mask(image, 10, 1, 0)
        result = bisect_unsharp_mask(image, 0.99, 1, 0)
        tock = time.time()
        #print tock - tick
        cv2.imshow('result', result)
        if key == 27: break

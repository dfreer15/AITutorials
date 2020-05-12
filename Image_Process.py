import cv2
import numpy as np
import copy


def blur_image(im):
    gaus_kernel = cv2.getGaussianKernel(20, 20)
    my_im_blur = cv2.filter2D(im, -1, gaus_kernel)
    cv2.imshow('blurred_image', my_im_blur)
    cv2.waitKey(0)
    return


def hor_edge(im):
    hor_kernel = np.array([[1, 0, -1],
                           [2, 0, -2],
                           [1, 0, -1]])
    my_im_hor = cv2.filter2D(im, -1, hor_kernel)
    cv2.imshow('hor_image', my_im_hor)
    cv2.waitKey(0)
    return my_im_hor


def vert_edge(im):
    vert_kernel = np.array([[1, 2, 1],
                            [0, 0, 0],
                            [-1, -2, -1]])
    my_im_vert = cv2.filter2D(im, -1, vert_kernel)
    cv2.imshow('vert_image', my_im_vert)
    cv2.waitKey(0)
    return my_im_vert


def color_pic(im):
    my_im_col = copy.copy(im)
    for i in range(im.shape[0]):
        for j in range(my_im.shape[1]):
            if im[i, j, 0] > 200 and im[i, j, 1] > 200 and im[i, j, 2] > 200:
                my_im_col[i, j] = [255, 255, 255]
            elif im[i, j, 0] > 165:
                my_im_col[i, j] = [230, 150, 20]
            elif im[i, j, 1] > 150:
                my_im_col[i, j] = [100, 200, 0]
            elif im[i, j, 2] > 150:
                my_im_col[i, j] = [0, 0, 255]
            else:
                if im[i, j, 0] > 100 and im[i, j, 1] > 100 and im[i, j, 2] > 100:
                    my_im_col[i, j] = [170, 150, 170]
                elif im[i, j, 0] > 80:
                    my_im_col[i, j] = [150, 70, 0]
                elif im[i, j, 1] > 80:
                    my_im_col[i, j] = [20, 130, 0]
                elif im[i, j, 2] > 80:
                    my_im_col[i, j] = [0, 0, 150]
                else:
                    my_im_col[i, j] = [50, 50, 50]

    cv2.imshow('colored_image', my_im_col)
    cv2.waitKey(0)


def hor_vert_features(im):
    im_hor = hor_edge(im)
    im_vert = vert_edge(im)
    im_hvf = im_hor + im_vert
    cv2.imshow('features', im_hvf)
    cv2.waitKey(0)

    return im_hvf


def smooth_untextured_regions(ref_im, proc_im, kernel_size=5):
    pad = int(kernel_size/2)
    start_y = pad
    end_y = ref_im.shape[0] - pad
    start_x = pad
    end_x = ref_im.shape[1] - pad

    feat_kernel = np.ones((kernel_size, kernel_size, 3))
    gaus_kernel = cv2.getGaussianKernel(kernel_size, 5)
    gaus_kernel_1 = np.dot(gaus_kernel, gaus_kernel.T)
    gaus_kernel_3 = np.array([gaus_kernel_1, gaus_kernel_1, gaus_kernel_1]).transpose([1, 2, 0])
    # cv2.waitKey(0)

    # Maybe look for other features in NEW photo? Where blue changes drastically?

    im_hvf = hor_vert_features(ref_im)
    sur_im = copy.copy(proc_im)
    k = np.zeros((im_hvf.shape[0], im_hvf.shape[1]))

    for i in range(start_y, end_y):
        for j in range(start_x, end_x):
            roi_hvf = im_hvf[i-pad:i+pad+1, j-pad:j+pad+1]
            roi_prod_feat = roi_hvf * feat_kernel
            k[i, j] = roi_prod_feat.sum()
            if k[i, j] < 45000:
                for l in [0, 1, 2]:
                    roi_proc_im = sur_im[i - pad:i + pad + 1, j - pad:j + pad + 1, l]
                    roi_proc_gaus = roi_proc_im*gaus_kernel_1
                    sur_im[i, j, l] = roi_proc_gaus.sum()
                    # print(sur_im[i, j, l])

    print(k[2:-2, 2:-2])

    cv2.imshow('smoothed_beaut_image', sur_im)
    cv2.waitKey(0)
    cv2.imshow('difference_from_smoothing', sur_im-proc_im)
    cv2.waitKey(0)


def beautify_pic(im):
    my_im_beaut = copy.copy(im)
    for i in range(my_im.shape[0]):
        for j in range(my_im.shape[1]):
            if im[i, j, 0] > 200 and im[i, j, 1] > 200 and im[i, j, 2] > 200:
                my_im_beaut[i, j] += np.array([30, 30, 30], dtype='uint8')
                for k in [0, 1, 2]:
                    if my_im_beaut[i, j, k] > 255 or my_im_beaut[i, j, k] < 40:
                        my_im_beaut[i, j, k] = 255
            elif im[i, j, 0] > 165 or im[i, j, 1] > 150:
                if i < im.shape[0]:
                    my_im_beaut[i, j] += np.array([50, 10, 10], dtype='uint8')
                else:
                    my_im_beaut[i, j] += np.array([20, 20, 20], dtype='uint8')
                for k in [0, 1, 2]:
                    if my_im_beaut[i, j, k] > 255 or my_im_beaut[i, j, k] < 50:
                        my_im_beaut[i, j, k] = 255
            elif im[i, j, 0] > 100 and im[i, j, 1] > 100 and im[i, j, 2] > 100:
                if i < 250:
                    my_im_beaut[i, j] += np.array([40, 10, 10], dtype='uint8')

    cv2.imshow('beaut_image', my_im_beaut)
    cv2.waitKey(0)

    smooth_untextured_regions(my_im, my_im_beaut, kernel_size=41)


filename = 'EileanDonan.jpg'

my_im = cv2.imread(filename)
cv2.imshow('original_image', my_im)
cv2.waitKey(0)

# blur_image(my_im)
# hor_edge(my_im)
# vert_edge(my_im)
# hor_vert_features(my_im)
# color_pic(my_im)
beautify_pic(my_im)







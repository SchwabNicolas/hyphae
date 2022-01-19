import binascii
import numpy as np
import scipy
import scipy.cluster


def dominant_color(img, nb_clusters=5, need_resize=False):
    if need_resize:
        img = img.resize((150, 150))

    img_arr = np.asarray(img)
    shape = img_arr.shape
    img_arr = img_arr.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

    codes, dist = scipy.cluster.vq.kmeans(img_arr, nb_clusters)

    vecs, dist = scipy.cluster.vq.vq(img_arr, codes)
    counts, bins = scipy.histogram(vecs, len(codes))

    index_max = scipy.argmax(counts)
    peak = codes[index_max]
    colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    return colour

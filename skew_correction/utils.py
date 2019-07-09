import urllib.request as urllib
import PIL.Image
import cv2
import numpy as np


def decode(scores, geometry, confidenceThreshold):
    """
    Decodes found rects according to confidence threshold
    """
    (numRows, numCols) = scores.shape[2:4]
    confidences = []
    rects = []
    baggage = []
    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        dTop = geometry[0, 0, y]
        dRight = geometry[0, 1, y]
        dBottom = geometry[0, 2, y]
        dLeft = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
        for x in range(0, numCols):
            if scoresData[x] < confidenceThreshold:
                continue

            confidences.append(float(scoresData[x]))

            (offsetX, offsetY) = (x * 4.0, y * 4.0)
            angle = anglesData[x]
            upperRight = (offsetX + dRight[x], offsetY - dTop[x])
            lowerRight = (offsetX + dRight[x], offsetY + dBottom[x])
            upperLeft = (offsetX - dLeft[x], offsetY - dTop[x])
            lowerLeft = (offsetX - dLeft[x], offsetY + dBottom[x])

            rects.append([
                int(upperLeft[0]),  # x
                int(upperLeft[1]),  # y
                int(lowerRight[0] - upperLeft[0]),  # w
                int(lowerRight[1] - upperLeft[1])  # h
            ])

            baggage.append({
                "offset": (offsetX, offsetY),
                "angle": angle,
                "upperRight": upperRight,
                "lowerRight": lowerRight,
                "upperLeft": upperLeft,
                "lowerLeft": lowerLeft,
                "dTop": dTop[x],
                "dRight": dRight[x],
                "dBottom": dBottom[x],
                "dLeft": dLeft[x]
            })

    return (rects, confidences, baggage)


def url_to_image(url):
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


def path_to_image(path):
    img = PIL.Image.open(path)
    return img


def decode_to_image(nparray):
    img = PIL.Image.fromarray(nparray, 'RGB')
    return img

import cv2
import numpy as np
from nms import nms
from .utils import decode, url_to_image, path_to_image
from .errors import ImageNotFoundException, ResourceNotFound
import os

class Skewer:

    def __init__(self, image_data=None, image_url=None, image_path=None):
        self.image = self._initiate_image(image_data=image_data, image_url=image_url, image_path=image_path)
        self.orig = self.image.copy()
        self.precalculated_angle = 0
        self.text_box_count = 0  # amount detected text boxes in image
        self.vertical_count = 0  # How many of boxes are vertical
        self.rotation_applied = False
        self.drawOn = self.image.copy()  # manipulated image copy for angle calculation

    def _initiate_image(self, image_data=None, image_url=None, image_path=None):
        if not any([image_url, image_path]) and not image_data.any():
            raise ImageNotFoundException("Couldn't find any image.")

        if image_url:
            image = url_to_image(image_url)
        elif image_path:
            image = path_to_image(image_path)
        elif image_data.any():
            image = image_data
        else:
            raise ImageNotFoundException("Couldn't find any image.")

        return image

    def draw_boxes(self, drawOn, boxes, ratioWidth, ratioHeight, color=(0, 255, 0), width=1):
        """
        Creates boxes of drawOn images for more accurate angle calculation. Color param is RGB format.
        """
        self.text_box_count = len(boxes)
        for (x, y, w, h) in boxes:

            if h > w:
                self.precalculated_angle = 90
                self.vertical_count += 1

            startX = int(x * ratioWidth)
            startY = int(y * ratioHeight)
            endX = int((x + w) * ratioWidth)
            endY = int((y + h) * ratioHeight)
            cv2.rectangle(drawOn, (startX, startY), (endX, endY), color, width)

    def detect_text(self, min_confidence=0.01, width=320, height=320):
        """
        Detects text fields according to EAST algoritm. Lookup east dataset and marks founded text fields.
        Width and Height should be multiple of 32. It is predefined condition for opencv (dnn) operations.
        """
        (origHeight, origWidth) = self.image.shape[:2]

        (newW, newH) = (width, height)
        ratioWidth = origWidth / float(newW)
        ratioHeight = origHeight / float(newH)

        self.image = cv2.resize(self.image, (newW, newH))
        (imageHeight, imageWidth) = self.image.shape[:2]

        layerNames = [
            "feature_fusion/Conv_7/Sigmoid",
            "feature_fusion/concat_3"
        ]
        try:
            path = os.path.abspath(os.path.dirname(__file__))
            net = cv2.dnn.readNet(path + '/resources/frozen_east_text_detection.pb')
        except FileNotFoundError:
            raise ResourceNotFound(
                """Frozen East Text Detector couldn't find in resources.
                For download to resource:
                >>> from skew_correction.data import download
                >>> download()
                
                or 
                
                $ python -c 'from skew_correction.data import download; download();'
                """
            )

        blob = cv2.dnn.blobFromImage(self.image, 1.0, (imageWidth, imageHeight), (123.68, 116.78, 103.94), swapRB=True,
                                     crop=False)

        net.setInput(blob)
        (scores, geometry) = net.forward(layerNames)

        confidenceThreshold = min_confidence
        nmsThreshold = 0.4
        (rects, confidences, baggage) = decode(scores, geometry, confidenceThreshold)

        offsets = []
        thetas = []
        for b in baggage:
            offsets.append(b['offset'])
            thetas.append(b['angle'])

        indicies = nms.boxes(
            rects,
            confidences,
            nms_function=nms.malisiewicz.nms,
            confidence_threshold=confidenceThreshold,
            nsm_threshold=nmsThreshold
        )

        indicies = np.array(indicies).reshape(-1)

        drawrects = np.array(rects)[indicies]

        self.draw_boxes(self.drawOn, drawrects, ratioWidth, ratioHeight, (0, 0, 0), 2)

    def calculate_angle(self):
        """
        calculates angle from manipulated image. ( drawOn )
        """
        gray = cv2.cvtColor(self.drawOn, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        # this part is cause of cv2.minAreaRect returns between (-90, 0)
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        return angle

    def rotate(self, angle):
        h, w = self.orig.shape[:2]
        image_center = (w / 2, h / 2)

        rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)
        cos_v = abs(rotation_mat[0, 0])
        sin_v = abs(rotation_mat[0, 1])
        # calculation of new image size
        result_w = int(h * sin_v + w * cos_v)
        result_h = int(h * cos_v + w * sin_v)

        rotation_mat[0, 2] += result_w / 2 - image_center[0]
        rotation_mat[1, 2] += result_h / 2 - image_center[1]

        rotated_image = cv2.warpAffine(self.orig, rotation_mat, (result_w, result_h))
        return rotated_image

    def is_rotated(self):
        return self.rotation_applied

    def get_rotated(self):
        self.detect_text()
        if float(self.vertical_count / self.text_box_count) < 0.5:
            angle = self.calculate_angle()
        else:
            angle = self.precalculated_angle
        if angle == 0:
            return None
        self.rotation_applied = True
        return self.rotate(angle)

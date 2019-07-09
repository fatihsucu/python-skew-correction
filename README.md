# python-skew-correction
Python Skew Corrector for Text Images


### Installation
#### With pypi
NOTE: This package isn't uploaded to pypi yet. After dynamic east detector implementation it will.
```
pip install python-skew-correction 
```
#### From source code
```
git clone https://github.com/fatihsucu/python-skew-correction.git

cd python-skew-correction
python setup.py install
```

### Example Usage
```
from skew_correction.skewer import Skewer
# image show
import cv2

skewer = Skewer(image_url="https;//some_image_url")

rotated = skewer.get_rotated()

if skewer.is_rotated(): # Returns true or false according to any skew operation
    cv2.imshow("Rotated image", rotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

```


#### Resources
```
https://www.pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/
https://www.pyimagesearch.com/2018/08/20/opencv-text-detection-east-text-detector/
```

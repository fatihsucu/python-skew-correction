from setuptools import setup

setup(
    name='python-skew-correction',
    version='0.1',
    description='Python Text Image Skew Correction',
    url='https://github.com/fatihsucu/python-skew-correction',
    author='Fatih Sucu',
    author_email='fatihsucu0@gmail.com',
    license='MIT',
    packages=['skew_correction'],
    install_requires=[
        "opencv-contrib-python", "numpy", "nms", "Pillow"
    ],
    zip_safe=False
)
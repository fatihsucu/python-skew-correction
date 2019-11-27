

class ImageNotFoundException(Exception):

    def __init__(self, message):
        self.message = message


class ResourceNotFound(Exception):
    def __init__(self, message):
        self.message = message
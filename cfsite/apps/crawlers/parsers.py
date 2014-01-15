from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    """ MLStripper
    ----------
    A simple class which strips tags from ML data.

    """
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return ''.join(self.fed)
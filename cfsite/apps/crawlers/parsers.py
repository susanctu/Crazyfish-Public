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


class MLTagDetector(HTMLParser):
    """ MLTagDetector
    ----------
    A simple class which detects the tags in ML data.

    """
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_starttag(self, tag, attrs):
        self.fed.append("<%s>" % tag)

    def handle_endtag(self, tag):
        self.fed.append("</%s>" % tag)

    def get_tags(self):
        return ''.join(self.fed)


class MLFormatter():
    """ MLFormatter
    ----------
    A simple class which turns a string into html data.

    """
    _formatted_string = ''

    def __init__(self):
        self._formatted_string = ''

    def feed(self, data_string):
        """ MLFormatter.feed()
        ----------
        @param data_string: a string of data which should be converted into
               html.
        @type data_string: str
        """
        split_str = data_string.split('\n')
        for fragment in split_str:
            if fragment:
                self._formatted_string += '<p>' + fragment + '</p>'
            else:
                self._formatted_string += '<br>'

    def get_formatted_string(self):
        return self._formatted_string
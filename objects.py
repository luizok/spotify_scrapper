class SpotifyMusic(object):

    def __init__(self, web_el):
        # Save important properties
        self.raw_text = web_el.text

        tokens = self.raw_text.split('\n')

        self.title = tokens[1]
        self.authors = tokens[2]
        self.album = tokens[3]
        self.duration = self.__convert_to_secs(tokens[4])

        super().__init__()

    def __convert_to_secs(self, duration_str):
        m, s = duration_str.split(':')

        return int(m) * 60 + int(s)

    def __str__(self):
        return f'<{self.title}: {self.album}: {self.authors}: {self.duration}>'

    __repr__ = __str__

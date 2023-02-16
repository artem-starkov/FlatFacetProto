class InputException(Exception):
    def __init__(self, bytes_):
        self.bytes_ = bytes_


class BrightsException(Exception):
    def __init__(self, omm_num, brights):
        self.omm_num = omm_num
        self.brights = brights
        super().__init__()

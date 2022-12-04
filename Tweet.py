class Tweet:

    def __init__(self, msg, loc):
        self.message = msg
        self.location = loc

    def __str__(self):
        return f"Message: {self.message}, Location: {self.location}"

    __repr__ = __str__
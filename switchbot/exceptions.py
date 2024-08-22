class APIError(Exception):
    """API exceptions, all specific exceptions inherits from it."""

    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop("request", None)
        if self.response is not None:
            self.query_id = self.response.headers["x-amzn-RequestId"]
        else:
            self.query_id = None
        super(APIError, self).__init__(*args, **kwargs)

    def __str__(self):
        if self.query_id:  # pragma: no cover
            return "{} \nAmzn-Request-ID: {}".format(super(APIError, self).__str__(), self.query_id)
        else:  # pragma: no cover
            return super(APIError, self).__str__()
class ServiceError(Exception):
    ...


class NotFound(ServiceError):
    def __init__(self, *args, detail: str):
        self.detail = detail
        super().__init__(*args)

    def __str__(self):
        return self.detail

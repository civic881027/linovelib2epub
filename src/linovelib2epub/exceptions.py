class LinovelibException(Exception):
    """
    Base exception class for Linovelib2epub library.
    """
    pass

class PageContentAbnormalException(LinovelibException):
    def __init__(self, message="Page content is abnormal"):
        super().__init__(message)


class EmptyTitleError(LinovelibException):
    def __init__(self, message = "The book title is empty"):
        super().__init__(message)

class EmptyArticleError(LinovelibException):
    def __init__(self, message = "The article tag can't be found"):
        super().__init__(message)

class NotIntactTextError(LinovelibException):
    def __init__(self, message="The text content is not intact"):
        super().__init__(message)


class CrawlStopped(LinovelibException):
    """The crawl ended early because the user asked it to stop."""
    def __init__(self, message="The crawl was stopped on request"):
        super().__init__(message)
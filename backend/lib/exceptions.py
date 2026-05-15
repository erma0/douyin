class CrawlerError(Exception):
    pass


class NetworkError(CrawlerError):
    pass


class AuthError(CrawlerError):
    pass


class VerifyCheckError(AuthError):
    pass

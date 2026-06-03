class OPEException(Exception):
    pass

class ClaimError(OPEException):
    pass

class VersionConflictError(OPEException):
    pass

class ValidationError(OPEException):
    pass

class NotFoundError(OPEException):
    pass

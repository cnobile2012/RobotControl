#
# central/utils/exceptions.py
#


class BaseGPIOException(Exception):
    def __init__(self, msg):
        super(BaseGPIOException, self).__init__(msg)


class InvalidPinNomenclatureException(BaseGPIOException):
    def __init__(self, pin):
        msg = ("Invalid pin nomenclature, found: {}, should be one of: "
               "P<conector>_<num> or GPIO<num>_<num>, or "
               "GPIO_<num>").format(pin)
        super(InvalidPinNomenclatureException, self).__init__(msg)


class InvalidDirectionException(BaseGPIOException):
    def __init__(self, pin):
        msg = ("Invalid direction, found: {}, should be one of: "
               "'in' or 'out'").format(pin)
        super(InvalidDirectionException, self).__init__(msg)


class InvalidArgumentsException(BaseGPIOException):
    def __init__(self, msg):
        super(InvalidArgumentsException, self).__init__(msg)

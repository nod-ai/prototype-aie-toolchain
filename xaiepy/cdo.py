import platform
import sys


if platform.system() != "Windows":
    from os import RTLD_GLOBAL, RTLD_NOW

    old = sys.getdlopenflags()
    try:
        sys.setdlopenflags(RTLD_GLOBAL | RTLD_NOW)
        from ._cdo import ffi
    finally:
        sys.setdlopenflags(old)
else:
    from ._cdo import ffi


@ffi.def_extern()
def cdo_BlockWrite32(Addr, pData, size):
    print(Addr, pData, size)


@ffi.def_extern()
def cdo_Write32(Addr, Data):
    print(Addr, Data)


@ffi.def_extern()
def cdo_MaskWrite32(Addr, Mask, Data):
    print(Addr, Mask, Data)


@ffi.def_extern()
def cdo_MaskPoll(Addr, Mask, Expected_Value, TimeoutInMS):
    print(Addr, Mask, Expected_Value, TimeoutInMS)


@ffi.def_extern()
def cdo_BlockSet32(Addr, Data, size):
    print(Addr, Data, size)

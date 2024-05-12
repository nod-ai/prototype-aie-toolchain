from _ctypes import Structure
from ctypes import c_int, c_bool, c_uint

from . import uint32_t, _lib, String

enum_byte_ordering = c_int

Little_Endian = 0

Big_Endian = Little_Endian + 1

enum_CDO_COMMAND = c_int

CDO_CMD_DMA_WRITE = 0x105

CDO_CMD_MASK_POLL64 = 0x106

CDO_CMD_MASK_WRITE64 = 0x107

CDO_CMD_WRITE64 = 0x108

CDO_CMD_NO_OPERATION = 0x111


class struct_cdoHeader(Structure):
    pass


struct_cdoHeader.__slots__ = [
    "NumWords",
    "IdentWord",
    "Version",
    "CDOLength",
    "CheckSum",
]
struct_cdoHeader._fields_ = [
    ("NumWords", uint32_t),
    ("IdentWord", uint32_t),
    ("Version", uint32_t),
    ("CDOLength", uint32_t),
    ("CheckSum", uint32_t),
]

cdoHeader = struct_cdoHeader


startCDOFileStream = _lib.get("startCDOFileStream", "cdecl")
startCDOFileStream.argtypes = [String]
startCDOFileStream.restype = None


endCurrentCDOFileStream = _lib.get("endCurrentCDOFileStream", "cdecl")
endCurrentCDOFileStream.argtypes = []
endCurrentCDOFileStream.restype = None


FileHeader = _lib.get("FileHeader", "cdecl")
FileHeader.argtypes = []
FileHeader.restype = None


EnAXIdebug = _lib.get("EnAXIdebug", "cdecl")
EnAXIdebug.argtypes = []
EnAXIdebug.restype = None


setEndianness = _lib.get("setEndianness", "cdecl")
setEndianness.argtypes = [c_bool]
setEndianness.restype = None


configureHeader = _lib.get("configureHeader", "cdecl")
configureHeader.argtypes = []
configureHeader.restype = None


getPadBytesForDmaWrCmdAlignment = _lib.get("getPadBytesForDmaWrCmdAlignment", "cdecl")
getPadBytesForDmaWrCmdAlignment.argtypes = [uint32_t]
getPadBytesForDmaWrCmdAlignment.restype = c_uint


insertNoOpCommand = _lib.get("insertNoOpCommand", "cdecl")
insertNoOpCommand.argtypes = [c_uint]
insertNoOpCommand.restype = None


insertDmaWriteCmdHdr = _lib.get("insertDmaWriteCmdHdr", "cdecl")
insertDmaWriteCmdHdr.argtypes = [uint32_t]
insertDmaWriteCmdHdr.restype = None


disableDmaCmdAlignment = _lib.get("disableDmaCmdAlignment", "cdecl")
disableDmaCmdAlignment.argtypes = []
disableDmaCmdAlignment.restype = None

cdoHeader = struct_cdoHeader

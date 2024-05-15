import json
import logging
import platform
from pathlib import Path

import numpy as np
from xaiepy import bootgen, xclbinutil
from xaiepy.cdo import (
    startCDOFileStream,
    FileHeader,
    configureHeader,
    endCurrentCDOFileStream,
    EnAXIdebug,
    setEndianness,
    Little_Endian,
)
from xaiepy.pyxrt import ert_cmd_state

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="%H:%M:%S",
)

from xaiepy import (
    XAie_Config,
    XAie_BackendType,
    XAie_PartitionProp,
    XAie_DevInst,
    XAie_CfgInitialize,
    XAie_LocType,
    XAie_LoadElf,
    XAie_SetupPartitionConfig,
    XAie_UpdateNpiAddr,
    XAie_CoreReset,
    XAie_CoreUnreset,
    XAie_LockSetValue,
    XAie_Lock,
    XAie_DmaDescInit,
    XAie_DmaSetAddrLen,
    XAie_DmaEnableBd,
    XAie_DmaWriteBd,
    XAie_DmaChannelSetStartQueue,
    XAie_DmaChannelEnable,
    XAie_StrmConnCctEnable,
    XAie_CoreEnable,
    StrmSwPortType,
    XAie_EnableAieToShimDmaStrmPort,
    XAie_DmaDesc,
)

if platform.system() != "Windows":
    from xaiepy import XAie_ErrorHandlingInit

XAIE_DEV_GEN_AIEML = 2
XAIE_BASE_ADDR = 0x40000000
XAIE_COL_SHIFT = 25
XAIE_ROW_SHIFT = 20
XAIE_SHIM_ROW = 0
XAIE_MEM_TILE_ROW_START = 1
XAIE_PARTITION_BASE_ADDR = 0x0
XAIE_TRANSACTION_DISABLE_AUTO_FLUSH = 0b0
DDR_AIE_ADDR_OFFSET = 0x80000000

col = 0
tile_0_0 = XAie_LocType(0, col)
tile_0_1 = XAie_LocType(1, col)
tile_0_2 = XAie_LocType(2, col)

configPtr = XAie_Config(
    XAIE_DEV_GEN_AIEML,
    XAIE_BASE_ADDR,
    XAIE_COL_SHIFT,
    XAIE_ROW_SHIFT,
    6,
    5,
    XAIE_SHIM_ROW,
    XAIE_MEM_TILE_ROW_START,
    1,
    (XAIE_MEM_TILE_ROW_START + 1),
    (6 - 1 - 1),
    XAie_PartitionProp(),
    XAie_BackendType.XAIE_IO_BACKEND_CDO,
)

devInst = XAie_DevInst()

XAie_SetupPartitionConfig(devInst, 0, 1, 1)
XAie_CfgInitialize(devInst, configPtr)
XAie_UpdateNpiAddr(devInst, 0)

EnAXIdebug()
setEndianness(Little_Endian)
cdo_fp = Path(__file__).parent.absolute() / "pi_cdo.bin"
startCDOFileStream(str(cdo_fp))
FileHeader()

if platform.system() != "Windows":
    XAie_ErrorHandlingInit(devInst)

XAie_LoadElf(devInst, tile_0_2, str(Path(__file__).parent.absolute() / "pi.elf"), False)

XAie_CoreReset(devInst, tile_0_2)
XAie_CoreUnreset(devInst, tile_0_2)
XAie_LockSetValue(devInst, tile_0_2, XAie_Lock(0, 1))
XAie_LockSetValue(devInst, tile_0_2, XAie_Lock(1, 0))

dmaTileBd = XAie_DmaDesc()
XAie_DmaDescInit(devInst, dmaTileBd, tile_0_2)
dmaTileBd.DmaMod.contents.SetLock(dmaTileBd, XAie_Lock(1, -1), XAie_Lock(0, 1), 1, 0)
XAie_DmaSetAddrLen(dmaTileBd, 1024, 4)
XAie_DmaEnableBd(dmaTileBd)
XAie_DmaWriteBd(devInst, dmaTileBd, tile_0_2, 0)
XAie_DmaChannelSetStartQueue(devInst, tile_0_2, 0, 1, 0, 1, 0)
XAie_DmaChannelEnable(devInst, tile_0_2, 0, 1)

XAie_StrmConnCctEnable(
    devInst, tile_0_0, StrmSwPortType.CTRL, 0, StrmSwPortType.SOUTH, 0
)
XAie_StrmConnCctEnable(
    devInst, tile_0_0, StrmSwPortType.NORTH, 0, StrmSwPortType.SOUTH, 2
)
XAie_StrmConnCctEnable(
    devInst, tile_0_1, StrmSwPortType.NORTH, 0, StrmSwPortType.SOUTH, 0
)
XAie_StrmConnCctEnable(
    devInst, tile_0_2, StrmSwPortType.DMA, 0, StrmSwPortType.SOUTH, 0
)
XAie_EnableAieToShimDmaStrmPort(devInst, tile_0_0, 2)
XAie_CoreEnable(devInst, tile_0_2)

configureHeader()
endCurrentCDOFileStream()

bif_fp = Path(__file__).parent.absolute() / "pi.bif"
with open(bif_fp, "w") as f:
    f.write(bootgen.emit_design_bif([cdo_fp]))

pdi_fp = Path(__file__).parent.absolute() / "pi.pdi"
bootgen.make_design_pdi(str(bif_fp), str(pdi_fp))
mem_top_json_fp = Path(__file__).parent.absolute() / "mem_topology.json"
with open(mem_top_json_fp, "w") as f:
    json.dump(xclbinutil.mem_topology, f)
aie_part_json_fp = Path(__file__).parent.absolute() / "aie_partition.json"
with open(aie_part_json_fp, "w") as f:
    json.dump(xclbinutil.emit_partition(pdi_fp, num_cols=1), f)
kernels_json_fp = Path(__file__).parent.absolute() / "kernels.json"
with open(kernels_json_fp, "w") as f:
    json.dump(xclbinutil.emit_design_kernel_json(), f)

pi_xclbin_fp = Path(__file__).parent.absolute() / "pi.xclbin"
xclbinutil.make_xclbin(
    str(mem_top_json_fp), str(aie_part_json_fp), str(kernels_json_fp), str(pi_xclbin_fp)
)

try:
    from xaiepy import pyxrt
except ImportError as e:
    assert (
            e.args[0]
            == "libxrt_coreutil.so: cannot open shared object file: No such file or directory"
    )
    raise ImportError(
        "Can't find libxrt_coreutil.so; you probably need to set LD_LIBRARY_PATH=/opt/xilinx/xrt/lib"
    )

_PROLOG = [
    0x00000011,
    0x01000405,
    0x01000100,
    0x0B590100,
    0x000055FF,
    0x00000001,
    0x00000010,
    0x314E5A5F,
    0x635F5F31,
    0x676E696C,
    0x39354E5F,
    0x6E693131,
    0x5F727473,
    0x64726F77,
    0x00004573,
    0x07BD9630,
    0x000055FF,
]

shim_instr_v = [
    0x06000100,
    0x00000000,
    0x00000001,
    0x00000000,
    0x00000000,
    0x00000000,
    0x80000000,
    0x00000000,
    0x00000000,
    0x02000000,
    0x02000000,
    0x0001D204,
    0x80000000,
    0x03000000,
    0x00010100,
]

instr_v = _PROLOG + shim_instr_v


def init_xrt_load_kernel(xclbin: Path, kernel_name):
    device = pyxrt.device(0)
    xclbin = pyxrt.xclbin(str(xclbin))
    xkernel = next(k for k in xclbin.get_kernels() if k.get_name() == kernel_name)
    device.register_xclbin(xclbin)
    context = pyxrt.hw_context(device, xclbin.get_uuid())
    kernel = pyxrt.kernel(context, xkernel.get_name())
    return device, kernel


device, kernel = init_xrt_load_kernel(pi_xclbin_fp, "MLIR_AIE")

instr_v = np.array(instr_v, dtype=np.uint32)

bo_instr = pyxrt.bo(device, len(instr_v) * 4, pyxrt.bo.cacheable, kernel.group_id(0))
bo_inout0 = pyxrt.bo(device, 1 * 4, pyxrt.bo.host_only, kernel.group_id(2))

inout0 = np.ones((1,), dtype=np.float32)

bo_instr.write(instr_v, 0)
bo_inout0.write(inout0, 0)

bo_instr.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)
bo_inout0.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

h = kernel(bo_instr, len(instr_v), bo_inout0)
assert h.wait() == ert_cmd_state.ERT_CMD_STATE_COMPLETED
bo_inout0.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)
entire_buffer = bo_inout0.read(4, 0).view(np.float32)
print(entire_buffer[0])
v = entire_buffer[0].item()
assert isinstance(v, float)
assert np.isclose(v, 3.14)
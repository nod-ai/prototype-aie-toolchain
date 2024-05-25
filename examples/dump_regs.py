from pathlib import Path

import numpy as np

from xaiepy import pyxrt
from xaiepy.pyxrt import ert_cmd_state


def init_xrt_load_kernel(xclbin: Path):
    device = pyxrt.device(0)
    xclbin = pyxrt.xclbin(str(xclbin))
    device.register_xclbin(xclbin)
    return device, xclbin


SIZE_1K = 1024
SIZE_4K = 4 * SIZE_1K
OFFSET_3K = 3 * SIZE_1K
XAIE_COL_SHIFT = 25
XAIE_ROW_SHIFT = 20


def get_tile_addr_here(c, r):
    return ((r & 0xFF) << XAIE_ROW_SHIFT) | ((c & 0xFF) << XAIE_COL_SHIFT)


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

DUMP_REGISTERS_OPCODE = 18

reg_offsets = [
    # corestatus
    0x00032004,
    # Stream_Switch_Master_Config_AIE_Core0
    0x0003F000,
    # module clock control
    0x00060000,
    # Event_Group_Stream_Switch_Enable
    0x00034518,
    # core le
    0x00031150,
    # Core_CR
    0x00031170,
    0x00030C00,
    0x00030C10,
]

registers_to_dump = [(DUMP_REGISTERS_OPCODE << 24) | len(reg_offsets)]

col, row = 0, 2
for reg in reg_offsets:
    abs_addr = reg + get_tile_addr_here(col, row)
    registers_to_dump.append(abs_addr & 0xFFFFFFFF)
    registers_to_dump.append((abs_addr >> 32) & 0xFFFFFFFF)


instr_v = _PROLOG + registers_to_dump
instr_v = np.array(instr_v, dtype=np.uint32)
inout0 = np.zeros((1,), dtype=np.float32)

device, xclbin = init_xrt_load_kernel(Path(__file__).parent.absolute() / "final.xclbin")

LEN = 128


def go():
    context = pyxrt.hw_context(device, xclbin.get_uuid())
    xkernel = next(k for k in xclbin.get_kernels() if k.get_name() == "MLIR_AIE")
    kernel = pyxrt.kernel(context, xkernel.get_name())

    bo_instr = pyxrt.bo(
        device, len(instr_v) * 4, pyxrt.bo.cacheable, kernel.group_id(0)
    )
    bo_instr.write(instr_v, 0)
    bo_instr.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

    bo_in = pyxrt.bo(device, LEN * 4, pyxrt.bo.host_only, kernel.group_id(2))
    bo_tmp = pyxrt.bo(device, LEN * 4, pyxrt.bo.host_only, kernel.group_id(3))
    bo_out = pyxrt.bo(device, LEN * 4, pyxrt.bo.host_only, kernel.group_id(4))
    bo_in.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)
    bo_tmp.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)
    bo_out.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

    h = kernel(bo_instr, len(instr_v), bo_in, bo_tmp, bo_out)
    assert h.wait() == ert_cmd_state.ERT_CMD_STATE_COMPLETED

    bo_reg_dumps = pyxrt.bo(device, SIZE_4K, pyxrt.bo.cacheable, kernel.group_id(0))
    bo_reg_dumps.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)
    reg_dumps = bo_reg_dumps.read(SIZE_1K, OFFSET_3K).view(np.uint32)
    print(list(reg_dumps))


go()

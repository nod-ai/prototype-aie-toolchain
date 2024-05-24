from pathlib import Path

import numpy as np

from xaiepy import pyxrt, xclbinutil
from xaiepy.pyxrt import ert_cmd_state

XCLBIN_FILE = Path(__file__).parent.absolute() / f"twokernels.xclbin"
# XCLBIN_FILE = Path(__file__).parent.absolute() / "pi.xclbin"
# xclbinutil.merge_xclbins(
#     "pi.xclbin", "twopi.xclbin", "twopi_kernel.json", str(XCLBIN_FILE)
# )


def init_xrt_load_kernel(xclbin: Path):
    device = pyxrt.device(0)
    xclbin = pyxrt.xclbin(str(xclbin))
    device.register_xclbin(xclbin)
    return device, xclbin


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
instr_v = np.array(instr_v, dtype=np.uint32)
inout0 = np.zeros((1,), dtype=np.float32)

device, xclbin = init_xrt_load_kernel(XCLBIN_FILE)


def go_pi():
    context = pyxrt.hw_context(device, xclbin.get_uuid())
    kernels = xclbin.get_kernels()
    pi_xkernel = next(k for k in kernels if k.get_name() == "pi")
    pi_kernel = pyxrt.kernel(context, pi_xkernel.get_name())

    pi_bo_instr = pyxrt.bo(
        device, len(instr_v) * 4, pyxrt.bo.cacheable, pi_kernel.group_id(0)
    )
    pi_bo_inout0 = pyxrt.bo(device, 1 * 4, pyxrt.bo.host_only, pi_kernel.group_id(2))

    pi_bo_instr.write(instr_v, 0)
    pi_bo_inout0.write(inout0, 0)

    pi_bo_instr.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)
    pi_bo_inout0.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

    h = pi_kernel(pi_bo_instr, len(instr_v), pi_bo_inout0)
    r = h.wait()
    print(r)
    # assert h.wait() == ert_cmd_state.ERT_CMD_STATE_COMPLETED
    pi_bo_inout0.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)
    entire_buffer = pi_bo_inout0.read(4, 0).view(np.float32)
    print(entire_buffer[0])


def go_twopi():
    context = pyxrt.hw_context(device, xclbin.get_uuid())

    kernels = xclbin.get_kernels()
    twopi_xkernel = next(k for k in kernels if k.get_name() == "twopi")

    twopi_kernel = pyxrt.kernel(context, twopi_xkernel.get_name())
    twopi_bo_instr = pyxrt.bo(
        device, len(instr_v) * 4, pyxrt.bo.cacheable, twopi_kernel.group_id(0)
    )
    twopi_bo_inout0 = pyxrt.bo(
        device, 1 * 4, pyxrt.bo.host_only, twopi_kernel.group_id(2)
    )

    twopi_bo_instr.write(instr_v, 0)
    twopi_bo_inout0.write(inout0, 0)

    twopi_bo_instr.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)
    twopi_bo_inout0.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

    h = twopi_kernel(twopi_bo_instr, len(instr_v), twopi_bo_inout0)
    r = h.wait()
    print(r)
    # assert h.wait() == ert_cmd_state.ERT_CMD_STATE_COMPLETED
    twopi_bo_inout0.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)
    entire_buffer = twopi_bo_inout0.read(4, 0).view(np.float32)
    print(entire_buffer[0])


go_pi()
go_twopi()
go_pi()
go_twopi()
go_pi()
go_twopi()
go_pi()
go_twopi()

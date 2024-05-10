import os
from pathlib import Path

import numpy as np

from xaiepy import pyxrt

os.environ["XILINX_XRT"] = "/opt/xilinx/xrt"
os.environ["LD_LIBRARY_PATH"] = "/opt/xilinx/xrt/lib"


def init_xrt_load_kernel(xclbin: Path, kernel_name):
    device = pyxrt.device(0)
    xclbin = pyxrt.xclbin(str(xclbin))
    xkernel = next(k for k in xclbin.get_kernels() if k.get_name() == kernel_name)
    device.register_xclbin(xclbin)
    context = pyxrt.hw_context(device, xclbin.get_uuid())
    kernel = pyxrt.kernel(context, xkernel.get_name())
    return device, kernel


device, kernel = init_xrt_load_kernel(
    Path(__file__).parent.absolute() / "pi.xclbin",
    "MLIR_AIE",
)

instr_v = [
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


instr_v = np.array(instr_v, dtype=np.uint32)

bo_instr = pyxrt.bo(device, len(instr_v) * 4, pyxrt.bo.cacheable, kernel.group_id(0))
bo_inout0 = pyxrt.bo(device, 1 * 4, pyxrt.bo.host_only, kernel.group_id(2))

inout0 = np.zeros((1,), dtype=np.float32)

bo_instr.write(instr_v, 0)
bo_inout0.write(inout0, 0)

bo_instr.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)
bo_inout0.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

h = kernel(bo_instr, len(instr_v), bo_inout0)
h.wait()
bo_inout0.sync(pyxrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)
entire_buffer = bo_inout0.read(4, 0).view(np.float32)
print(entire_buffer[0])
v = entire_buffer[0].item()
assert isinstance(v, float)
assert np.isclose(v, 3.14)

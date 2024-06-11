from pathlib import Path

import numpy as np
from filelock import FileLock
from xaiepy.xrt import XCLBin, list_kernels

# don't forget LD_LIBRARY_PATH=/opt/xilinx/xrt/lib:/usr/lib/x86_64-linux-gnu


M = K = N = 64

TEST = "basic_matrix_multiplication_matrix_vector"
WORKDIR = Path(__file__).parent.absolute() / TEST / "module_dummy1_amdaie_xclbin_fb"
NPU_INSTS_FP = f"{WORKDIR}/module_dummy1_amdaie_xclbin_fb.npu.txt"
XCLBIN_PATH = f"{WORKDIR}/module_dummy1_amdaie_xclbin_fb.xclbin"
KERNEL_NAME = "dummy2"
NUM_ARGS = 3

with open(NPU_INSTS_FP, "r") as f:
    npu_insts = list(map(lambda n: int(n, 16), f.readlines()))

instr_v = np.array(npu_insts, dtype=np.uint32)

with open(NPU_INSTS_FP, "r") as f:
    npu_insts = list(map(lambda n: int(n, 16), f.readlines()))

list_kernels(XCLBIN_PATH)

with FileLock("/tmp/npu.lock"):
    xclbin = XCLBin(XCLBIN_PATH, KERNEL_NAME)
    views = xclbin.mmap_buffers([(M, K), (K,), (M,)], np.float32)

    xclbin.load_npu_instructions(npu_insts)

    A = np.ones((M, K), dtype=np.float32)
    B = 2 * np.ones((K,), dtype=np.float32)
    C = np.zeros((M,), dtype=np.float32)

    wraps = list(map(np.asarray, views))
    np.copyto(wraps[0], A, casting="no")
    np.copyto(wraps[1], B, casting="no")
    np.copyto(wraps[2], C, casting="no")

    xclbin.sync_buffers_to_device()
    xclbin.run()
    print("Running kernel")
    xclbin.wait(30)
    xclbin.sync_buffers_from_device()

    print(wraps)
    assert np.allclose(A @ B, wraps[2])

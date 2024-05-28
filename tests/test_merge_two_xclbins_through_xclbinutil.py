#! /usr/bin/env python
from pathlib import Path

from xaiepy.xclbinutil import merge_two_xclbins


def test_merge():
    merge_two_xclbins(
        "module_matmul_large_dispatch_0_amdaie_xclbin_fb/module_matmul_large_dispatch_0_amdaie_xclbin_fb.xclbin",
        "module_matmul_small_1_dispatch_0_amdaie_xclbin_fb/module_matmul_small_1_dispatch_0_amdaie_xclbin_fb.xclbin",
        "module_matmul_small_1_dispatch_0_amdaie_xclbin_fb/kernels.json",
        "twokernels.xclbin",
    )
    assert Path("twokernels.xclbin").exists()

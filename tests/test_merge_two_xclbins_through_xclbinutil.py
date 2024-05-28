from pathlib import Path

import pytest

from xaiepy.xclbinutil import merge_two_xclbins, XCLBIN_PATH

if XCLBIN_PATH is None:
    pytest.skip(allow_module_level=True)


def test_merge():
    merge_two_xclbins(
        "module_matmul_large_dispatch_0_amdaie_xclbin_fb/module_matmul_large_dispatch_0_amdaie_xclbin_fb.xclbin",
        "module_matmul_small_1_dispatch_0_amdaie_xclbin_fb/module_matmul_small_1_dispatch_0_amdaie_xclbin_fb.xclbin",
        "module_matmul_small_1_dispatch_0_amdaie_xclbin_fb/kernels.json",
        "twokernels.xclbin",
    )
    assert Path("twokernels.xclbin").exists()

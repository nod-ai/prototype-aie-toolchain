import importlib
import json
import os
import platform
import random
import subprocess
import sys
from pathlib import Path

from ._xclbinutil import *

mem_topology = {
    "mem_topology": {
        "m_count": "2",
        "m_mem_data": [
            {
                "m_type": "MEM_DRAM",
                "m_used": "1",
                "m_sizeKB": "0x10000",
                "m_tag": "HOST",
                "m_base_address": "0x4000000",
            },
            {
                "m_type": "MEM_DRAM",
                "m_used": "1",
                "m_sizeKB": "0xc000",
                "m_tag": "SRAM",
                "m_base_address": "0x4000000",
            },
        ],
    }
}


def pdi_spec(pdi_fp: Path, kernel_ids=None, uuid=None, pdi_id=None):
    if kernel_ids is None:
        kernel_ids = ["0x100"]
    if uuid is None:
        uuid = random.randint(2222, 9999)
    if pdi_id is None:
        pdi_id = "0x01"
    return {
        "uuid": "00000000-0000-0000-0000-00000000" + str(uuid),
        "file_name": str(pdi_fp),
        "cdo_groups": [
            {
                "name": "DPU",
                "type": "PRIMARY",
                # https://github.com/Xilinx/XRT/blob/727fcd7a5314d6d00c5a718206899da09b205a5a/src/runtime_src/core/include/xclbin.h#L588
                "pdi_id": pdi_id,
                "dpu_kernel_ids": kernel_ids,
                # https://github.com/Xilinx/XRT/blob/727fcd7a5314d6d00c5a718206899da09b205a5a/src/runtime_src/core/include/xclbin.h#L590
                "pre_cdo_groups": ["0xC1"],
            }
        ],
    }


def emit_partition(pdis: list, start_columns=None, num_cols=None):
    assert isinstance(pdis, list)
    assert num_cols is not None or start_columns is not None
    if start_columns is None:
        start_columns = list(range(1, 6 - num_cols))

    return {
        "aie_partition": {
            "name": "QoS",
            "operations_per_cycle": "2048",
            "inference_fingerprint": "23423",
            "pre_post_fingerprint": "12345",
            "partition": {
                "column_width": num_cols,
                "start_columns": start_columns,
            },
            "PDIs": pdis,
        }
    }


def kernel_spec(
    kernel_name="MLIR_AIE",
    # does this really need to be in hex?
    kernel_id="0x100",
    # TODO: no clue
    buffer_args=None,
):
    if buffer_args is None:
        buffer_args = ["in", "tmp", "out"]

    arguments = [
        {
            "name": "instr",
            "memory-connection": "SRAM",
            "address-qualifier": "GLOBAL",
            "type": "char *",
            "offset": "0x00",
        },
        {
            "name": "ninstr",
            "address-qualifier": "SCALAR",
            "type": "uint64_t",
            "offset": "0x08",
        },
    ]

    offset = 0x10
    for buf in buffer_args:
        arg = {
            "name": buf,
            "memory-connection": "HOST",
            "address-qualifier": "GLOBAL",
            "type": "char *",
            "offset": str(hex(offset)),
        }
        arguments.append(arg)
        offset += 0x8
    return {
        "name": kernel_name,
        "type": "dpu",
        "extended-data": {
            "subtype": "DPU",
            # TODO: no clue
            "functional": "1",
            "dpu_kernel_id": kernel_id,
        },
        "arguments": arguments,
        "instances": [{"name": kernel_name}],
    }


def emit_design_kernel_json(kernel_specs):
    return {"ps-kernels": {"kernels": kernel_specs}}


def do_run(command):
    print(" ".join(command), file=sys.stderr)
    subprocess.check_call(command)


_EXE_EXT = ".exe" if platform.system() == "Windows" else ""
_XCLBIN_PATH = Path(__file__).parent / ("xclbinutil" + _EXE_EXT)
XCLBIN_PATH = Path(os.getenv("XCLBIN_PATH", _XCLBIN_PATH))
assert XCLBIN_PATH.exists(), "couldn't find xclbinutil"


def get_dpu_kernel_id_from_pdi(pdi):
    assert len(pdi["cdo_groups"]) == 1, "only cdo group in lhs supported"
    assert (
        len(pdi["cdo_groups"][0]["dpu_kernel_ids"]) == 1
    ), "only dpu_kernel_id in lhs supported"
    # return the whole list so we can update it in-place
    return pdi["cdo_groups"][0]["dpu_kernel_ids"]


def update_pdi_abs_path(pdi, partition_fp):
    if not os.path.isabs(pdi["file_name"]):
        abs_path = (Path(partition_fp).parent / pdi["file_name"]).resolve()
        assert abs_path.exists(), f"couldn't find {pdi['file_name']} at {abs_path}"
        pdi["file_name"] = str(abs_path)

    return pdi


def dump_partition_json(xclbin_fp: Path, output_partition_json_fp: Path):
    do_run(
        [
            str(XCLBIN_PATH),
            "--dump-section",
            "AIE_PARTITION:JSON:" + str(output_partition_json_fp),
            "--force",
            "--input",
            str(xclbin_fp),
            "-vtq",
        ],
    )


def merge_two_xclbins(
    lhs_xclbin_fp, rhs_xclbin_fp, rhs_kernel_json_fp, output_xclbin_fp
):
    lhs_partition_json_fp = Path(lhs_xclbin_fp).parent / "lhs_partition.json"
    dump_partition_json(lhs_xclbin_fp, lhs_partition_json_fp)

    with open(lhs_partition_json_fp) as f:
        lhs_partition = json.load(f)
    assert (
        len(lhs_partition["aie_partition"]["PDIs"]) == 1
    ), "only 1 pdi in lhs supported"
    lhs_pdi = lhs_partition["aie_partition"]["PDIs"][0]
    lhs_pdi = update_pdi_abs_path(lhs_pdi, lhs_partition_json_fp)
    lhs_dpu_kernel_id = get_dpu_kernel_id_from_pdi(lhs_pdi)

    rhs_partition_json_fp = Path(rhs_xclbin_fp).parent / "rhs_partition.json"
    dump_partition_json(rhs_xclbin_fp, rhs_partition_json_fp)
    with open(rhs_partition_json_fp) as f:
        rhs_partition = json.load(f)
    assert (
        len(rhs_partition["aie_partition"]["PDIs"]) == 1
    ), "only 1 pdi in lhs supported"
    rhs_pdi = rhs_partition["aie_partition"]["PDIs"][0]
    rhs_pdi = update_pdi_abs_path(rhs_pdi, rhs_partition_json_fp)
    rhs_dpu_kernel_id = get_dpu_kernel_id_from_pdi(rhs_pdi)

    with open(rhs_kernel_json_fp) as rhs_kernel_json_f:
        rhs_kernel_json = json.load(rhs_kernel_json_f)
    assert (
        len(rhs_kernel_json["ps-kernels"]["kernels"]) == 1
    ), "only 1 rhs kernel supported"
    assert (
        rhs_kernel_json["ps-kernels"]["kernels"][0]["extended-data"]["dpu_kernel_id"]
        == rhs_dpu_kernel_id[0]
    )

    if lhs_dpu_kernel_id == rhs_dpu_kernel_id:
        rhs_kernel_json["ps-kernels"]["kernels"][0]["extended-data"][
            "dpu_kernel_id"
        ] = rhs_dpu_kernel_id[0] = str(hex(int(rhs_dpu_kernel_id[0], 16) + 1))

    updated_rhs_kernel_json_fp = (
        Path(rhs_kernel_json_fp).parent / "updated_rhs_kernel.json"
    )
    with open(updated_rhs_kernel_json_fp, "w") as updated_rhs_kernel_json_f:
        json.dump(rhs_kernel_json, updated_rhs_kernel_json_f, indent=2)

    lhs_partition["aie_partition"]["PDIs"].extend(
        rhs_partition["aie_partition"]["PDIs"]
    )

    with open("merged_partition.json", "w") as f:
        json.dump(lhs_partition, f, indent=2)

    do_run(
        [
            str(XCLBIN_PATH),
            "--input",
            str(lhs_xclbin_fp),
            "--add-kernel",
            str(updated_rhs_kernel_json_fp),
            "--add-replace-section",
            "AIE_PARTITION:JSON:" + "merged_partition.json",
            "--force",
            "--output",
            str(output_xclbin_fp),
            "-vtq",
        ],
    )

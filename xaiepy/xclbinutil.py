import random
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

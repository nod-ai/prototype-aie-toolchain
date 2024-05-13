import random

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


def emit_partition(pdi_fp, kernel_id="0x901", start_columns=None, num_cols=None):
    assert num_cols is not None or start_columns is not None
    if start_columns is None:
        start_columns = list(range(1, 6 - num_cols))

    uuid = random.randint(2222, 9999)
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
            "PDIs": [
                {
                    "uuid": "00000000-0000-0000-0000-00000000" + str(uuid),
                    "file_name": str(pdi_fp),
                    "cdo_groups": [
                        {
                            "name": "DPU",
                            "type": "PRIMARY",
                            "pdi_id": "0x01",
                            "dpu_kernel_ids": [kernel_id],
                            "pre_cdo_groups": ["0xC1"],
                        }
                    ],
                }
            ],
        }
    }


def emit_design_kernel_json(
    kernel_name="MLIR_AIE",
    kernel_id="0x901",
    instance_name="MLIRAIE",
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
        "ps-kernels": {
            "kernels": [
                {
                    "name": kernel_name,
                    "type": "dpu",
                    "extended-data": {
                        "subtype": "DPU",
                        "functional": "1",
                        "dpu_kernel_id": kernel_id,
                    },
                    "arguments": arguments,
                    "instances": [{"name": instance_name}],
                }
            ]
        }
    }

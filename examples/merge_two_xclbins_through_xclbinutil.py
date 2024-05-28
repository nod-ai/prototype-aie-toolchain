#! /usr/bin/env python

import json
import os
import subprocess
import sys
from pathlib import Path


def do_run(command):
    print(" ".join(command), file=sys.stderr)
    subprocess.check_call(command)


XCLBIN_PATH = "/opt/xilinx/xrt/bin/xclbinutil"


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


def dump_partition_json(xclbin_fp, output_partition_json_fp):
    do_run(
        [
            XCLBIN_PATH,
            "--dump-section",
            "AIE_PARTITION:JSON:" + str(output_partition_json_fp),
            "--force",
            "--input",
            str(xclbin_fp),
            "-vtq",
        ],
    )


def main(lhs_xclbin_fp, rhs_xclbin_fp, rhs_kernel_json_fp, output_xclbin_fp):
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
            XCLBIN_PATH,
            "--input",
            lhs_xclbin_fp,
            "--add-kernel",
            str(updated_rhs_kernel_json_fp),
            "--add-replace-section",
            "AIE_PARTITION:JSON:" + "merged_partition.json",
            "--force",
            "--output",
            output_xclbin_fp,
            "-vtq",
        ],
    )


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("lhs_xclbin_fp")
    # parser.add_argument("rhs_kernel_json_fp")
    # parser.add_argument("output_xclbin_fp")
    # args = parser.parse_args()
    # main(args.lhs_xclbin_fp, args.rhs_kernel_json_fp, args.output_xclbin_fp)
    main(
        "module_matmul_large_dispatch_0_amdaie_xclbin_fb/module_matmul_large_dispatch_0_amdaie_xclbin_fb.xclbin",
        "module_matmul_small_1_dispatch_0_amdaie_xclbin_fb/module_matmul_small_1_dispatch_0_amdaie_xclbin_fb.xclbin",
        "module_matmul_small_1_dispatch_0_amdaie_xclbin_fb/kernels.json",
        "twokernels.xclbin",
    )

#! /usr/bin/env python

import argparse
import json
import subprocess
import sys


def do_run(command):
    print(" ".join(command), file=sys.stderr)
    subprocess.check_call(command)


XCLBIN_PATH = "/opt/xilinx/xrt/bin/xclbinutil"


def main(lhs_xclbin_fp, rhs_partition_json_fp, rhs_kernel_json_fp, output_xclbin_fp):
    do_run(
        [
            XCLBIN_PATH,
            "--dump-section",
            "AIE_PARTITION:JSON:" + "lhs_partition.json",
            "--force",
            "--input",
            lhs_xclbin_fp,
            "-vtq",
        ],
    )
    with open("lhs_partition.json") as f:
        lhs_partition = json.load(f)

    with open(rhs_partition_json_fp) as f:
        rhs_partition = json.load(f)

    lhs_partition["aie_partition"]["PDIs"] = lhs_partition["aie_partition"][
        "PDIs"
    ].extend(rhs_partition["aie_partition"]["PDIs"])

    with open("merged_partition.json", "w") as f:
        json.dump(rhs_partition, f, indent=2)

    do_run(
        [
            XCLBIN_PATH,
            "--input",
            lhs_xclbin_fp,
            "--add-kernel",
            rhs_kernel_json_fp,
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
        "pi.xclbin",
        "twopi_aie_partition.json",
        "twopi_kernel.json",
        "twokernels.xclbin",
    )

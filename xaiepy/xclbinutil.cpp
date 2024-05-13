//
// Created by mlevental on 5/12/24.
//

#include <pybind11/pybind11.h>

#include "XclBinUtilities.h"
#include "XclBinClass.h"

using namespace pybind11::literals;

PYBIND11_MODULE(_xclbinutil, m) {
    m.def("make_xclbin",
          [](const std::string &memTopologyJsonFilePath, const std::string &aiePartitionFilePath,
             const std::string &kernelJsonFilePath,
             const std::string &outputFilePath) {
              XclBin xclBin;
              ParameterSectionData memTopSec("MEM_TOPOLOGY:JSON:" + memTopologyJsonFilePath);
              xclBin.addReplaceSection(memTopSec);
              ParameterSectionData aiePartSec("AIE_PARTITION:JSON:" + aiePartitionFilePath);
              xclBin.addReplaceSection(aiePartSec);
              xclBin.addKernels(kernelJsonFilePath);
              xclBin.writeXclBinBinary(outputFilePath, false);
          }, "mem_topology_json_fp"_a, "aie_partition_json_fp"_a, "kernel_json_fp"_a, "output_fp"_a);
}
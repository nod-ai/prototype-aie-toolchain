//
// Created by mlevental on 5/12/24.
//

#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <pybind11/pybind11.h>

#include "KernelUtilities.h"
#include "SectionAIEPartition.h"
#include "XclBinClass.h"
#include "XclBinUtilities.h"

using namespace pybind11::literals;
namespace XUtil = XclBinUtilities;
namespace pt = boost::property_tree;
namespace py = pybind11;

std::string dumpPtToJSON(const pt::ptree &tree) {
  std::ostringstream oss;
  pt::write_json(oss, tree);
  return oss.str();
}

std::string dumpPtToXML(const pt::ptree &tree) {
  std::ostringstream oss;
  pt::write_xml(oss, tree);
  return oss.str();
}

void getSectionPayload(const XclBin *pXclBin, axlf_section_kind kind,
                       boost::property_tree::ptree &ptPayLoad) {
  ptPayLoad.clear();
  Section *pSection = pXclBin->findSection(kind);

  if (pSection != nullptr)
    pSection->getPayload(ptPayLoad);
}

void putSectionPayload(XclBin *pXclBin, axlf_section_kind kind,
                       const boost::property_tree::ptree &ptPayLoad) {
  // Is there anything to update, if not then exit early
  if (ptPayLoad.empty())
    return;

  Section *pSection = pXclBin->findSection(kind);

  if (pSection == nullptr) {
    pSection = Section::createSectionObjectOfKind(kind);
    pXclBin->addSection(pSection);
  }

  pSection->readJSONSectionImage(ptPayLoad);
}

PYBIND11_MODULE(_xclbinutil, m) {
  m.def(
      "make_xclbin",
      [](const std::string &memTopologyJsonFp,
         const std::string &aiePartitionFp, const std::string &kernelJsonFp,
         const std::string &outputFp) {
        XclBin xclBin;
        ParameterSectionData memTopSec("MEM_TOPOLOGY:JSON:" +
                                       memTopologyJsonFp);
        xclBin.addReplaceSection(memTopSec);
        ParameterSectionData aiePartSec("AIE_PARTITION:JSON:" + aiePartitionFp);
        xclBin.addReplaceSection(aiePartSec);
        xclBin.addKernels(kernelJsonFp);
        xclBin.writeXclBinBinary(outputFp, false);
      },
      "mem_topology_json_fp"_a, "aie_partition_json_fp"_a, "kernel_json_fp"_a,
      "output_fp"_a);

  m.def(
      "merge_xclbins",
      [](const std::string &lhsXclBinFp, const std::string &rhsXclBinFp,
         const std::string &rhsKernelJsonFp,
         const std::string &outputXclBinFp) {
        XclBin lhsXclBin, rhsXclBin;
        lhsXclBin.readXclBinBinary(lhsXclBinFp);
        rhsXclBin.readXclBinBinary(rhsXclBinFp);

        pt::ptree lhsEmbedded, lhsIPLayout, lhsConnectivity, lhsMemTopology;
        getSectionPayload(&lhsXclBin, EMBEDDED_METADATA, lhsEmbedded);
        getSectionPayload(&lhsXclBin, IP_LAYOUT, lhsIPLayout);
        getSectionPayload(&lhsXclBin, CONNECTIVITY, lhsConnectivity);
        getSectionPayload(&lhsXclBin, MEM_TOPOLOGY, lhsMemTopology);

        pt::ptree rhsKernelJson;
        pt::read_json(rhsKernelJsonFp, rhsKernelJson);

        for (const auto &kernel :
             rhsKernelJson.get_child("ps-kernels.kernels")) {
          XUtil::addKernel(kernel.second, /*isFixedPS*/ true, lhsEmbedded);
          XUtil::addKernel(kernel.second, lhsMemTopology, lhsIPLayout,
                           lhsConnectivity);
        }

        putSectionPayload(&lhsXclBin, EMBEDDED_METADATA, lhsEmbedded);
        putSectionPayload(&lhsXclBin, IP_LAYOUT, lhsIPLayout);
        putSectionPayload(&lhsXclBin, CONNECTIVITY, lhsConnectivity);
        putSectionPayload(&lhsXclBin, MEM_TOPOLOGY, lhsMemTopology);

        std::string aiePartSection = "AIE_PARTITION:JSON:";
        ParameterSectionData lhsPsd(aiePartSection + "lhs.json");
        lhsXclBin.dumpSection(lhsPsd);
        ParameterSectionData rhsPsd(aiePartSection + "rhs.json");
        rhsXclBin.dumpSection(rhsPsd);

        pt::ptree lhsPt, rhsPt;
        pt::read_json("lhs.json", lhsPt);
        pt::read_json("rhs.json", rhsPt);

        for (const auto &pdi : rhsPt.get_child("aie_partition.PDIs"))
          lhsPt.get_child("aie_partition.PDIs").push_back({"", pdi.second});

        pt::write_json("merged.json", lhsPt);
        ParameterSectionData mergedPsd(aiePartSection + "merged.json");
        lhsXclBin.addReplaceSection(mergedPsd);

        XUtil::createMemoryBankGrouping(lhsXclBin);
        lhsXclBin.writeXclBinBinary(outputXclBinFp,
                                    /*bSkipUUIDInsertion*/ false);
      },
      "lhs_xclbin_fp"_a, "rhs_xclbin_fp"_a, "rhs_kernel_json_fp"_a,
      "output_xclbin_fp"_a);
}
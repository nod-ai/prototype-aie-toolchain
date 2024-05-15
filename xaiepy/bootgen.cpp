//
// Created by mlevental on 5/12/24.
//

#include <pybind11/pybind11.h>

#include "bootimage.h"

using namespace pybind11::literals;

PYBIND11_MODULE(_bootgen, m) {
    m.def("make_design_pdi", [](std::string bifFilePath, std::string outputFilePath, bool debug) {
        Options options;
        if (debug)
            options.SetLogLevel(LogLevel::TRACE);
        options.SetArchType(Arch::VERSAL);
        options.SetBifFilename(bifFilePath);
        options.SetOverwrite(true);
        options.InsertOutputFileNames(outputFilePath);
        BIF_File bif(bifFilePath);
        bif.Process(options);
    }, "bif_fp"_a, "output_fp"_a, "debug"_a = false);
}
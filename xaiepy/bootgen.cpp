//
// Created by mlevental on 5/12/24.
//

#include <pybind11/pybind11.h>

#include "bootimage.h"

using namespace pybind11::literals;

PYBIND11_MODULE(_bootgen, m) {
    m.def("make_design_pdi", [](std::string bifFileName, std::string outputFileName, bool debug) {
        Options options;
        if (debug)
            options.SetLogLevel(LogLevel::TRACE);
        options.SetArchType(Arch::VERSAL);
        options.SetBifFilename(bifFileName);
        options.SetOverwrite(true);
        options.InsertOutputFileNames(outputFileName);
        BIF_File bif(bifFileName);
        bif.Process(options);
    }, "bif_filename"_a, "output_filename"_a, "debug"_a = false);
}
from textwrap import dedent

from cffi import FFI


def build_ffi(tmpdir, target):
    ffibuilder = FFI()

    # these are for generating the trampolines and the ones below are the actual symbols
    ffibuilder.cdef(
        """
        extern "Python+C" void cdo_Write32(uint64_t, uint32_t);
        extern "Python+C" void cdo_MaskWrite32(uint64_t , uint32_t, uint32_t);
        extern "Python+C" void cdo_MaskPoll(uint64_t , uint32_t, uint32_t, uint32_t);
        extern "Python+C" void cdo_BlockWrite32(uint64_t, const uint32_t*, uint32_t);
        extern "Python+C" void cdo_BlockSet32(uint64_t, uint32_t, uint32_t);
    """
    )
    ffibuilder.set_source(
        "_cdo",
        dedent(
            r"""
            #if defined(_WIN32) || defined(__CYGWIN__)
                // Windows visibility declarations.
                #define CAPI_EXPORTED __declspec(dllexport)
            #else
                // Non-windows: use visibility attributes.
                #define CAPI_EXPORTED __attribute__((visibility("default")))
            #endif        
            CAPI_EXPORTED void cdo_Write32(uint64_t, uint32_t);
            CAPI_EXPORTED void cdo_MaskWrite32(uint64_t , uint32_t, uint32_t);
            CAPI_EXPORTED void cdo_MaskPoll(uint64_t , uint32_t, uint32_t, uint32_t);
            CAPI_EXPORTED void cdo_BlockWrite32(uint64_t, const uint32_t*, uint32_t);
            CAPI_EXPORTED void cdo_BlockSet32(uint64_t, uint32_t, uint32_t);
            """
        ),
    )
    ffibuilder.compile(tmpdir=tmpdir, target=target, verbose=True)

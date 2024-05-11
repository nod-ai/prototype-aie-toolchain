import os
import platform
import sys
from argparse import Namespace
from glob import glob
from pathlib import Path
from textwrap import dedent

from ctypesgen import parser as core_parser, processor
from ctypesgen.ctypedescs import CtypesStruct, CtypesBitfield, CtypesEnum
from ctypesgen.expressions import ConstantExpressionNode, ExpressionNode
from ctypesgen.printer_python import WrapperPrinter
from ctypesgen.printer_python.printer import LIBRARYLOADER_PATH


def find_names_in_modules(modules):
    names = set()
    for module in modules:
        try:
            mod = __import__(module)
        except Exception:
            pass
        else:
            names.update(dir(mod))
    return names


class _WrapperPrinter(WrapperPrinter):
    def __init__(self, outpath, options, data):
        self.file = open(outpath, "w") if outpath else sys.stdout
        self.options = options

        if (
            self.options.strip_build_path
            and self.options.strip_build_path[-1] != os.path.sep
        ):
            self.options.strip_build_path += os.path.sep

        if not self.options.embed_preamble and outpath:
            self._copy_preamble_loader_files(outpath)

        self.print_header()
        self.file.write("\n")

        # before everything else
        self.file.write("from .typed_ctypes_enum import *\n")
        self.file.write("from .cdo import *\n")

        self.print_preamble()
        self.file.write("\n")

        self.print_loader()
        self.file.write("\n")

        self.print_group(self.options.libraries, "libraries", self.print_library)
        self.print_group(self.options.modules, "modules", self.print_module)

        method_table = {
            "function": self.print_function,
            "macro": self.print_macro,
            "struct": self.print_struct,
            "struct-body": self.print_struct_members,
            "typedef": self.print_typedef,
            "variable": self.print_variable,
            "enum": self.print_enum,
            "constant": self.print_constant,
            "undef": self.print_undef,
        }

        for kind, desc in data.output_order:
            if desc.included:
                r = method_table[kind](desc)
                if kind == {"constant", "variable"} and not r:
                    continue
                self.file.write("\n")

        self.print_group(
            self.options.inserted_files, "inserted files", self.insert_file
        )
        self.strip_prefixes()

    def srcinfo(self, src):
        return

    def print_fixed_function(self, function):
        CC = "stdcall" if function.attrib.get("stdcall", False) else "cdecl"
        if function.source_library:
            self.file.write(
                '{PN} = _libs["{L}"].get("{CN}", "{CC}")\n'.format(
                    L=function.source_library,
                    CN=function.c_name(),
                    PN=function.py_name(),
                    CC=CC,
                )
            )
        else:
            self.file.write(
                '{PN} = _lib.get("{CN}", "{CC}")\n'.format(
                    CN=function.c_name(), PN=function.py_name(), CC=CC
                )
            )

        # Argument types
        self.file.write(
            "%s.argtypes = [%s]\n"
            % (
                function.py_name(),
                ", ".join([a.py_string() for a in function.argtypes]),
            )
        )

        # Return value
        if function.restype.py_string() == "String":
            self.file.write(
                "if sizeof(c_int) == sizeof(c_void_p):\n"
                "    {PN}.restype = ReturnString\n"
                "else:\n"
                "    {PN}.restype = {RT}\n"
                "    {PN}.errcheck = ReturnString\n".format(
                    PN=function.py_name(), RT=function.restype.py_string()
                )
            )
        else:
            self.file.write(
                "%s.restype = %s\n" % (function.py_name(), function.restype.py_string())
            )

    def print_variable(self, variable):
        return

    def print_library(self, library):
        self.file.write(
            '_lib = _libs["%s"] = load_library("%s")\n' % (library, library)
        )

    seen_enum_variants = set()

    def print_constant(self, constant):
        if constant.name in self.seen_enum_variants:
            return False
        self.file.write("%s = %s" % (constant.name, constant.value.py_string(False)))
        return True

    def print_enum(self, enum):
        enum_variant, node = enum.members[0]
        assert isinstance(node, ConstantExpressionNode)
        self.file.write(
            dedent(
                f"""\
        class {enum.ctype.tag}(CEnumeration):
            {enum_variant} = {node.py_string(False)}
        """
            )
        )
        self.seen_enum_variants.add(enum_variant)
        for i, (enum_variant, node) in enumerate(enum.members[1:], start=1):
            if i + 1 < len(enum.members):
                nl = "\n"
            else:
                nl = ""
            self.file.write(f"    {enum_variant} = {node.py_string(False)}{nl}")
            self.seen_enum_variants.add(enum_variant)

    def print_struct_members(self, struct):
        if struct.opaque:
            return

        # is this supposed to be packed?
        if struct.attrib.get("packed", False):
            aligned = struct.attrib.get("aligned", [1])
            assert (
                len(aligned) == 1
            ), "cgrammar gave more than one arg for aligned attribute"
            aligned = aligned[0]
            if isinstance(aligned, ExpressionNode):
                # TODO: for non-constant expression nodes, this will fail:
                aligned = aligned.evaluate(None)
            self.file.write(
                "{}_{}._pack_ = {}\n".format(struct.variety, struct.tag, aligned)
            )

        # handle unnamed fields.
        unnamed_fields = []
        names = set([x[0] for x in struct.members])
        anon_prefix = "unnamed_"
        n = 1
        for mi in range(len(struct.members)):
            mem = list(struct.members[mi])
            if mem[0] is None:
                while True:
                    name = "%s%i" % (anon_prefix, n)
                    n += 1
                    if name not in names:
                        break
                mem[0] = name
                names.add(name)
                if type(mem[1]) is CtypesStruct:
                    unnamed_fields.append(name)
                struct.members[mi] = mem

        self.file.write("%s_%s.__slots__ = [\n" % (struct.variety, struct.tag))
        for name, ctype in struct.members:
            self.file.write("    '%s',\n" % name)
        self.file.write("]\n")

        if len(unnamed_fields) > 0:
            self.file.write("%s_%s._anonymous_ = [\n" % (struct.variety, struct.tag))
            for name in unnamed_fields:
                self.file.write("    '%s',\n" % name)
            self.file.write("]\n")

        self.file.write("%s_%s._fields_ = [\n" % (struct.variety, struct.tag))
        for name, ctype in struct.members:
            if isinstance(ctype, CtypesBitfield):
                self.file.write(
                    "    ('%s', %s, %s),\n"
                    % (name, ctype.py_string(), ctype.bitfield.py_string(False))
                )
            else:
                ct = ctype.py_string()
                if isinstance(ctype, CtypesEnum):
                    ct = ctype.tag
                self.file.write("    ('%s', %s),\n" % (name, ct))
        self.file.write("]\n")

    def print_typedef(self, typedef):
        ct = typedef.ctype.py_string()
        if isinstance(typedef.ctype, CtypesEnum):
            ct = typedef.ctype.tag
        self.file.write("%s = %s" % (typedef.name, ct))

    def print_loader(self):
        self.file.write("_libs = {}\n")
        self.file.write("_libdirs = %s\n\n" % self.options.compile_libdirs)
        self.file.write("# Begin loader\n\n")
        if self.options.embed_preamble:
            with open(LIBRARYLOADER_PATH, "r") as loader_file:
                self.file.write(loader_file.read())
        else:
            self.file.write("from .ctypes_loader import *\n")
        self.file.write("\n# End loader\n\n")
        self.file.write("from pathlib import Path\n")
        self.file.write(
            "add_library_search_dirs([%s])"
            % ", ".join([d for d in self.options.runtime_libdirs])
        )
        self.file.write("\n")


EXCLUDED_HEADERS = set()

if platform.system() == "Windows":
    EXCLUDED_HEADERS.add("xaie_interrupt.h")


def generate(xaie_build_include_dir: Path, output: Path, elf_include_dir: Path):
    headers = list(
        filter(
            lambda f: Path(f).name not in EXCLUDED_HEADERS,
            glob(f'{xaie_build_include_dir / "xaiengine" / "*.h"}'),
        )
    )

    if platform.system() == "Darwin":
        cc = "clang"
    elif platform.system() in {"Linux", "Windows"}:
        cc = "gcc"
    else:
        raise NotImplementedError(f"unknown platform {platform.system()}")

    cpp_defines = ["__AIECDO__"]
    if platform.system() in {"Darwin", "Windows"}:
        # knockout xlnx-ai-engine.h which include <linux>
        cpp_defines.append("_UAPI_AI_ENGINE_H_")

    args = Namespace(
        headers=headers,
        all_headers=False,
        allow_gnu_c=False,
        builtin_symbols=False,
        compile_libdirs=[str(Path(__file__).parent)],
        cpp=f"{cc} -E -I {elf_include_dir}",
        cpp_defines=cpp_defines,
        cpp_undefines=[],
        debug_level=0,
        embed_preamble=True,
        exclude_symbols=[
            "XAie_MapIrqIdToCols",
            "XAie_DisableErrorInterrupts",
            "XAie_BacktrackErrorInterrupts",
        ],
        header_template=None,
        # blows up file
        include_macros=False,
        include_search_paths=[],
        include_symbols=[],
        include_undefs=True,
        inserted_files=[],
        libraries=["xaie"],
        modules=[],
        no_gnu_types=False,
        no_load_library=False,
        no_python_types=False,
        no_stddef_types=False,
        optimize_lexer=False,
        other_headers=[],
        other_known_names=[],
        output=None,
        output_language="py",
        runtime_libdirs=["str(Path(__file__).parent)"],
        save_preprocessed_headers=None,
        show_all_errors=False,
        show_long_errors=False,
        show_macro_warnings=True,
        strip_build_path=None,
        strip_prefixes=[],
        universal_libdirs=[],
    )

    args.compile_libdirs = args.compile_libdirs + args.universal_libdirs
    args.runtime_libdirs = args.runtime_libdirs + args.universal_libdirs
    args.other_known_names = find_names_in_modules(args.modules)

    descriptions = core_parser.parse(args.headers, args)
    processor.process(descriptions, args)

    _WrapperPrinter(str(output.absolute()), args, descriptions)

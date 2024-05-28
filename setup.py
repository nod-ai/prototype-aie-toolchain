import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from pprint import pprint

from cmake import cmake_executable_path
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.editable_wheel import editable_wheel


class CMakeExtension(Extension):
    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[], optional=True)
        self.sourcedir = os.fspath(Path(sourcedir).resolve())


def check_env(build):
    return os.environ.get(build, 0) in {"1", "true", "True", "ON", "YES"}


EDITABLE = False


class editable_wheel(editable_wheel):
    def run(self):
        global EDITABLE
        EDITABLE = True
        super().run()


class CMakeBuild(build_ext):
    def build_extension(self, ext: CMakeExtension) -> None:
        HERE = Path(__file__).parent.absolute()
        ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)
        extdir = ext_fullpath.parent.resolve()
        cfg = "Debug" if check_env("DEBUG") else "Release"

        if EDITABLE:
            extdir = HERE

        cmake_generator = os.environ.get("CMAKE_GENERATOR", "Ninja")

        # make windows happy
        PYTHON_EXECUTABLE = str(Path(sys.executable))
        CMAKE_MODULE_PATH = str(HERE / "third_party" / "aie-rt" / "fal" / "cmake")
        if platform.system() == "Windows":
            PYTHON_EXECUTABLE = PYTHON_EXECUTABLE.replace("\\", "\\\\")
            # i have no clue - cmake parses these at different points...?
            CMAKE_MODULE_PATH = CMAKE_MODULE_PATH.replace("\\", "//")

        cmake_args = [
            f"-B{build_temp}",
            f"-G{cmake_generator}",
            f"-DCMAKE_MODULE_PATH={CMAKE_MODULE_PATH}",
            "-DCMAKE_PLATFORM_NO_VERSIONED_SONAME=ON",
            f"-DOUTPUT_DIR={extdir / PACKAGE_NAME}",
            f"-DPython3_EXECUTABLE={PYTHON_EXECUTABLE}",
            f"-DPY_VERSION={'.'.join(map(str, sys.version_info[:2]))}",
            f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
            "-DCMAKE_C_VISIBILITY_PRESET=default",
        ]

        if platform.system() == "Windows":
            cmake_args += [
                "-DCMAKE_C_COMPILER=cl",
                "-DCMAKE_CXX_COMPILER=cl",
                "-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=ON",
                "-DCMAKE_SUPPORT_WINDOWS_EXPORT_ALL_SYMBOLS=ON",
            ]
            if check_env("OPENSSL_ROOT_DIR"):
                OPENSSL_ROOT_DIR = os.getenv(
                    "OPENSSL_ROOT_DIR", "C:\\Program Files\\OpenSSL"
                )
                cmake_args += [f"-DOPENSSL_ROOT_DIR={OPENSSL_ROOT_DIR}"]

        if "CMAKE_ARGS" in os.environ:
            cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]

        build_args = []
        if self.compiler.compiler_type == "msvc":
            single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})
            contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})
            if not single_config and not contains_arch:
                PLAT_TO_CMAKE = {
                    "win32": "Win32",
                    "win-amd64": "x64",
                    "win-arm32": "ARM",
                    "win-arm64": "ARM64",
                }
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]
            if not single_config:
                build_args += ["--config", cfg]

        if platform.system() == "Darwin":
            cmake_args += ["-DBUILD_PYXRT=OFF"]
            osx_version = os.getenv("OSX_VERSION", "11.6")
            cmake_args += [f"-DCMAKE_OSX_DEPLOYMENT_TARGET={osx_version}"]
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
            if archs:
                cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

        if "PARALLEL_LEVEL" not in os.environ:
            build_args += [f"-j{str(2 * os.cpu_count())}"]
        else:
            build_args += [f"-j{os.environ.get('PARALLEL_LEVEL')}"]

        env = os.environ.copy()
        print("ENV", pprint(os.environ), file=sys.stderr)
        print("CMAKE_ARGS", cmake_args, file=sys.stderr)
        print(f"{cmake_executable_path=}", file=sys.stderr)

        CMAKE_EXE_PATH = cmake_executable_path / "bin" / "cmake"
        subprocess.run(
            [str(CMAKE_EXE_PATH), ext.sourcedir, *cmake_args],
            cwd=build_temp,
            check=True,
            env=env,
        )
        subprocess.run(
            [CMAKE_EXE_PATH, "--build", ".", "--target", "xaie", *build_args],
            cwd=build_temp,
            check=True,
            env=env,
        )
        subprocess.run(
            [CMAKE_EXE_PATH, "--build", ".", "--target", "xclbinutil", *build_args],
            cwd=build_temp,
            check=True,
            env=env,
        )

        sys.path.append(str(HERE))
        from util import gen_xaie_ctypes

        gen_xaie_ctypes.generate(
            build_temp / "include",
            extdir / PACKAGE_NAME / "__init__.py",
            elf_include_dir=HERE / "third_party" / "bootgen",
        )


PACKAGE_NAME = "xaiepy"

build_temp = Path.cwd() / "build" / "temp"
if not build_temp.exists():
    build_temp.mkdir(parents=True)


EXE_EXT = ".exe" if platform.system() == "Windows" else ""

setup(
    name=PACKAGE_NAME,
    author="Maksim Levental",
    author_email="maksim.levental@gmail.com",
    long_description_content_type="text/markdown",
    ext_modules=[CMakeExtension(PACKAGE_NAME, sourcedir=".")],
    cmdclass={"editable_wheel": editable_wheel, "build_ext": CMakeBuild},
    zip_safe=False,
    packages=[PACKAGE_NAME],
    package_data={PACKAGE_NAME: ["xclbinutil" + EXE_EXT]},
    include_package_data=True,
    install_requires=[
        str(ir.requirement)
        for ir in parse_requirements("requirements-dev.txt", session=PipSession())
    ],
    python_requires=">=3.8",
)

# xaiepy
AIE-RT + Python

# Downloading/installing

## Release

```shell
$ pip install xaiepy -f https://github.com/nod-ai/prototype-aie-toolchain/releases/expanded_assets/release
```

## Dev

```shell
$ pip install xaiepy -f https://github.com/nod-ai/prototype-aie-toolchain/releases/expanded_assets/dev
```

# Demo

```shell
$ python examples/basic.py

opcode='XAIE_IO_WRITE'
reg_off=000000000021d000
val=0
mask=000000000fffc000

opcode='XAIE_IO_WRITE'
reg_off=000000000021d020
val=0
mask=000000000fffc000

opcode='XAIE_IO_WRITE'
reg_off=000000000021d040
val=0
mask=000000000fffc000
```

# Development

## Gotchas

If **ON WINDOWS** you're having trouble with 

```shell
CMake Error at C:/Users/maksim/miniconda3/envs/xaiepy/Lib/site-packages/cmake/data/share/cmake-3.29/Modules/FindPackageHandleStandardArgs.cmake:230 (message):
  Could NOT find OpenSSL, try to set the path to OpenSSL root folder in the
  system variable OPENSSL_ROOT_DIR (missing: OPENSSL_CRYPTO_LIBRARY) (found
  version "3.3.0")
```

you probably have the win32 developer shell open; open the `x64 Native Tools Command Prompt for VS` instead ([or copy the settings from the win32 powershell to a new link](https://developercommunity.visualstudio.com/t/the-developer-powershell-for-vs-2022-should-use-x6/1568773#T-N10609425)) 🤦.

**Note**: `setup.py` expects OpenSSL to be installed @ `C:\Program Files\OpenSSL`.
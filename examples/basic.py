from pathlib import Path

from xaiepy import (
    XAie_Config,
    XAie_BackendType,
    XAie_PartitionProp,
    XAie_DevInst,
    XAie_CfgInitialize,
    XAie_StartTransaction,
    XAie_ExportTransactionInstance,
    XAie_TxnInst,
    XAie_LocType,
    XAie_DmaUpdateBdAddr,
    XAie_TxnOpcode,
    XAie_LoadElf,
)

XAIE_DEV_GEN_AIEML = 2
XAIE_BASE_ADDR = 0x40000000
XAIE_COL_SHIFT = 25
XAIE_ROW_SHIFT = 20
XAIE_SHIM_ROW = 0
XAIE_MEM_TILE_ROW_START = 1
XAIE_PARTITION_BASE_ADDR = 0x0
XAIE_TRANSACTION_DISABLE_AUTO_FLUSH = 0b0
DDR_AIE_ADDR_OFFSET = 0x80000000

config = XAie_Config(
    XAIE_DEV_GEN_AIEML,
    XAIE_BASE_ADDR,
    XAIE_COL_SHIFT,
    XAIE_ROW_SHIFT,
    6,
    5,
    XAIE_SHIM_ROW,
    XAIE_MEM_TILE_ROW_START,
    1,
    (XAIE_MEM_TILE_ROW_START + 1),
    (6 - 1 - 1),
    XAie_PartitionProp(),
    XAie_BackendType.XAIE_IO_BACKEND_CDO,
)


dev_inst = XAie_DevInst()
XAie_CfgInitialize(dev_inst, config)

XAie_StartTransaction(dev_inst, XAIE_TRANSACTION_DISABLE_AUTO_FLUSH)

col, row = 0, 2
tile_loc = XAie_LocType(row, col)
XAie_DmaUpdateBdAddr(dev_inst, tile_loc, 0, 0)
XAie_DmaUpdateBdAddr(dev_inst, tile_loc, 0, 1)
XAie_DmaUpdateBdAddr(dev_inst, tile_loc, 0, 2)

XAie_LoadElf(
    dev_inst, tile_loc, str(Path(__file__).parent.absolute() / "core_0_2.elf"), False
)

txn_inst: XAie_TxnInst = XAie_ExportTransactionInstance(dev_inst)

offsets = [0x21D000, 0x21D020, 0x21D040]
masks = [0xFFFC000, 0xFFFC000, 0xFFFC000]

for i in range(3):
    op = txn_inst.contents.CmdBuf[i]
    opcode = XAie_TxnOpcode._reverse_map_[op.Opcode.value]
    reg_off = op.RegOff
    mask = op.Mask
    val = op.Value

    print(f"{opcode=}")
    print(f"{reg_off=:016x}")
    print(f"{val=}")
    print(f"{mask=:016x}")
    print()

    assert (
        opcode == "XAIE_IO_WRITE"
        and reg_off == offsets[i]
        and mask == masks[i]
        and val == 0
    )

i = 4
op = txn_inst.contents.CmdBuf[i]
opcode = XAie_TxnOpcode._reverse_map_[op.Opcode.value]
reg_off = op.RegOff
data_ptr = op.DataPtr
size = op.Size

print(f"{opcode=}")
print(f"{reg_off=:016x}")
print(f"{data_ptr=:016x}")
print(f"{size}")
print()

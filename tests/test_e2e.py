from pathlib import Path

from xaiepy import (
    XAie_Config,
    XAie_BackendType,
    XAie_PartitionProp,
    XAie_DevInst,
    XAie_CfgInitialize,
    XAie_LocType,
    XAie_LoadElf,
    XAie_SetupPartitionConfig,
    XAie_UpdateNpiAddr,
    XAie_CoreReset,
    XAie_CoreUnreset,
    XAie_LockSetValue,
    XAie_Lock,
    XAie_DmaDescInit,
    XAie_DmaSetAddrLen,
    XAie_DmaEnableBd,
    XAie_DmaWriteBd,
    XAie_DmaChannelSetStartQueue,
    XAie_DmaChannelEnable,
    XAie_StrmConnCctEnable,
    XAie_CoreEnable,
    StrmSwPortType,
    XAie_EnableAieToShimDmaStrmPort,
    XAie_DmaDesc,
    XAie_StartTransaction,
    XAie_ExportTransactionInstance,
    XAie_TxnOpcode,
    _XAie_Txn_Submit,
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

configPtr = XAie_Config(
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

devInst = XAie_DevInst()

XAie_SetupPartitionConfig(devInst, 0, 1, 1)
XAie_CfgInitialize(devInst, configPtr)
# XAie_ErrorHandlingInit(devInst)


def test_transaction():
    XAie_StartTransaction(devInst, XAIE_TRANSACTION_DISABLE_AUTO_FLUSH)

    XAie_UpdateNpiAddr(devInst, 0)

    col = 0
    tile_0_0 = XAie_LocType(0, col)
    tile_0_1 = XAie_LocType(1, col)
    tile_0_2 = XAie_LocType(2, col)

    XAie_LoadElf(
        devInst, tile_0_2, str(Path(__file__).parent.absolute() / "core_0_2.elf"), False
    )

    XAie_CoreReset(devInst, tile_0_2)
    XAie_CoreUnreset(devInst, tile_0_2)
    XAie_LockSetValue(devInst, tile_0_2, XAie_Lock(0, 1))
    XAie_LockSetValue(devInst, tile_0_2, XAie_Lock(1, 0))

    dmaTileBd = XAie_DmaDesc()
    XAie_DmaDescInit(devInst, dmaTileBd, tile_0_2)
    dmaTileBd.DmaMod.contents.SetLock(
        dmaTileBd, XAie_Lock(1, -1), XAie_Lock(0, 1), 1, 0
    )
    XAie_DmaSetAddrLen(dmaTileBd, 1024, 4)
    XAie_DmaEnableBd(dmaTileBd)
    XAie_DmaWriteBd(devInst, dmaTileBd, tile_0_2, 0)
    XAie_DmaChannelSetStartQueue(devInst, tile_0_2, 0, 1, 0, 1, 0)
    XAie_DmaChannelEnable(devInst, tile_0_2, 0, 1)

    XAie_StrmConnCctEnable(
        devInst, tile_0_0, StrmSwPortType.CTRL, 0, StrmSwPortType.SOUTH, 0
    )
    XAie_StrmConnCctEnable(
        devInst, tile_0_0, StrmSwPortType.NORTH, 0, StrmSwPortType.SOUTH, 2
    )
    XAie_StrmConnCctEnable(
        devInst, tile_0_1, StrmSwPortType.NORTH, 0, StrmSwPortType.SOUTH, 0
    )
    XAie_StrmConnCctEnable(
        devInst, tile_0_2, StrmSwPortType.DMA, 0, StrmSwPortType.SOUTH, 0
    )
    XAie_EnableAieToShimDmaStrmPort(devInst, tile_0_0, 2)
    XAie_CoreEnable(devInst, tile_0_2)

    txn_inst = XAie_ExportTransactionInstance(devInst)
    _XAie_Txn_Submit(devInst, txn_inst)

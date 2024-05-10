"""
Pybind11 module for XRT
"""
from __future__ import annotations
import numpy
import typing
import typing_extensions
__all__ = ['XCL_BO_FLAGS_NONE', 'alert', 'bo', 'critical', 'debug', 'device', 'emergency', 'enumerate_devices', 'error', 'ert_cmd_state', 'hw_context', 'info', 'kernel', 'log_message', 'notice', 'run', 'uuid', 'warning', 'xclBOSyncDirection', 'xclbin', 'xclbinip_vector', 'xclbinkernel_vector', 'xclbinmem_vector', 'xrt_info_device', 'xrt_msg_level']
class bo:
    """
    Represents a buffer object
    """
    class flags:
        """
        Buffer object creation flags
        
        Members:
        
          normal
        
          cacheable
        
          device_only
        
          host_only
        
          p2p
        
          svm
        """
        __members__: typing.ClassVar[dict[str, bo.flags]]  # value = {'normal': <flags.normal: 0>, 'cacheable': <flags.cacheable: 16777216>, 'device_only': <flags.device_only: 268435456>, 'host_only': <flags.host_only: 536870912>, 'p2p': <flags.p2p: 1073741824>, 'svm': <flags.svm: 134217728>}
        cacheable: typing.ClassVar[bo.flags]  # value = <flags.cacheable: 16777216>
        device_only: typing.ClassVar[bo.flags]  # value = <flags.device_only: 268435456>
        host_only: typing.ClassVar[bo.flags]  # value = <flags.host_only: 536870912>
        normal: typing.ClassVar[bo.flags]  # value = <flags.normal: 0>
        p2p: typing.ClassVar[bo.flags]  # value = <flags.p2p: 1073741824>
        svm: typing.ClassVar[bo.flags]  # value = <flags.svm: 134217728>
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    cacheable: typing.ClassVar[bo.flags]  # value = <flags.cacheable: 16777216>
    device_only: typing.ClassVar[bo.flags]  # value = <flags.device_only: 268435456>
    host_only: typing.ClassVar[bo.flags]  # value = <flags.host_only: 536870912>
    normal: typing.ClassVar[bo.flags]  # value = <flags.normal: 0>
    p2p: typing.ClassVar[bo.flags]  # value = <flags.p2p: 1073741824>
    svm: typing.ClassVar[bo.flags]  # value = <flags.svm: 134217728>
    @typing.overload
    def __init__(self, arg0: device, arg1: int, arg2: bo.flags, arg3: int) -> None:
        """
        Create a buffer object with specified properties
        """
    @typing.overload
    def __init__(self, arg0: bo, arg1: int, arg2: int) -> None:
        """
        Create a sub-buffer of an existing buffer object of specifed size and offset in the existing buffer
        """
    def address(self) -> int:
        """
        Return the device physical address of the buffer object
        """
    def map(self) -> memoryview:
        """
        Create a byte accessible memory view of the buffer object
        """
    def read(self, arg0: int, arg1: int) -> numpy.ndarray[numpy.int8]:
        """
        Read from the buffer object requested number of bytes starting from specified offset
        """
    def size(self) -> int:
        """
        Return the size of the buffer object
        """
    @typing.overload
    def sync(self, arg0: xclBOSyncDirection, arg1: int, arg2: int) -> None:
        """
        Synchronize (DMA or cache flush/invalidation) the buffer in the requested direction
        """
    @typing.overload
    def sync(self, arg0: xclBOSyncDirection) -> None:
        """
        Sync entire buffer content in specified direction.
        """
    def write(self, arg0: typing_extensions.Buffer, arg1: int) -> None:
        """
        Write the provided data into the buffer object starting at specified offset
        """
class device:
    """
    Abstraction of an acceleration device
    """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: int) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: str) -> None:
        ...
    def get_info(self, arg0: xrt_info_device) -> str:
        """
        Obtain the device properties and sensor information
        """
    def get_xclbin_uuid(self) -> uuid:
        """
        Return the UUID object representing the xclbin loaded on the device
        """
    @typing.overload
    def load_xclbin(self, arg0: str) -> uuid:
        """
        Load an xclbin given the path to the device
        """
    @typing.overload
    def load_xclbin(self, arg0: "xrt::xclbin") -> uuid:
        """
        Load the xclbin to the device
        """
    def register_xclbin(self, arg0: "xrt::xclbin") -> uuid:
        """
        Register an xclbin with the device
        """
class ert_cmd_state:
    """
    Kernel execution status
    
    Members:
    
      ERT_CMD_STATE_NEW
    
      ERT_CMD_STATE_QUEUED
    
      ERT_CMD_STATE_COMPLETED
    
      ERT_CMD_STATE_ERROR
    
      ERT_CMD_STATE_ABORT
    
      ERT_CMD_STATE_SUBMITTED
    
      ERT_CMD_STATE_TIMEOUT
    
      ERT_CMD_STATE_NORESPONSE
    
      ERT_CMD_STATE_SKERROR
    
      ERT_CMD_STATE_SKCRASHED
    """
    ERT_CMD_STATE_ABORT: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_ABORT: 6>
    ERT_CMD_STATE_COMPLETED: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_COMPLETED: 4>
    ERT_CMD_STATE_ERROR: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_ERROR: 5>
    ERT_CMD_STATE_NEW: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_NEW: 1>
    ERT_CMD_STATE_NORESPONSE: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_NORESPONSE: 9>
    ERT_CMD_STATE_QUEUED: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_QUEUED: 2>
    ERT_CMD_STATE_SKCRASHED: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_SKCRASHED: 11>
    ERT_CMD_STATE_SKERROR: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_SKERROR: 10>
    ERT_CMD_STATE_SUBMITTED: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_SUBMITTED: 7>
    ERT_CMD_STATE_TIMEOUT: typing.ClassVar[ert_cmd_state]  # value = <ert_cmd_state.ERT_CMD_STATE_TIMEOUT: 8>
    __members__: typing.ClassVar[dict[str, ert_cmd_state]]  # value = {'ERT_CMD_STATE_NEW': <ert_cmd_state.ERT_CMD_STATE_NEW: 1>, 'ERT_CMD_STATE_QUEUED': <ert_cmd_state.ERT_CMD_STATE_QUEUED: 2>, 'ERT_CMD_STATE_COMPLETED': <ert_cmd_state.ERT_CMD_STATE_COMPLETED: 4>, 'ERT_CMD_STATE_ERROR': <ert_cmd_state.ERT_CMD_STATE_ERROR: 5>, 'ERT_CMD_STATE_ABORT': <ert_cmd_state.ERT_CMD_STATE_ABORT: 6>, 'ERT_CMD_STATE_SUBMITTED': <ert_cmd_state.ERT_CMD_STATE_SUBMITTED: 7>, 'ERT_CMD_STATE_TIMEOUT': <ert_cmd_state.ERT_CMD_STATE_TIMEOUT: 8>, 'ERT_CMD_STATE_NORESPONSE': <ert_cmd_state.ERT_CMD_STATE_NORESPONSE: 9>, 'ERT_CMD_STATE_SKERROR': <ert_cmd_state.ERT_CMD_STATE_SKERROR: 10>, 'ERT_CMD_STATE_SKCRASHED': <ert_cmd_state.ERT_CMD_STATE_SKCRASHED: 11>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class hw_context:
    """
    A hardware context associates an xclbin with hardware resources.
    """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: "xrt::device", arg1: uuid) -> None:
        ...
class kernel:
    """
    Represents a set of instances matching a specified name
    """
    class cu_access_mode:
        """
        Compute unit access mode
        
        Members:
        
          exclusive
        
          shared
        
          none
        """
        __members__: typing.ClassVar[dict[str, kernel.cu_access_mode]]  # value = {'exclusive': <cu_access_mode.exclusive: 0>, 'shared': <cu_access_mode.shared: 1>, 'none': <cu_access_mode.none: 2>}
        exclusive: typing.ClassVar[kernel.cu_access_mode]  # value = <cu_access_mode.exclusive: 0>
        none: typing.ClassVar[kernel.cu_access_mode]  # value = <cu_access_mode.none: 2>
        shared: typing.ClassVar[kernel.cu_access_mode]  # value = <cu_access_mode.shared: 1>
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    exclusive: typing.ClassVar[kernel.cu_access_mode]  # value = <cu_access_mode.exclusive: 0>
    none: typing.ClassVar[kernel.cu_access_mode]  # value = <cu_access_mode.none: 2>
    shared: typing.ClassVar[kernel.cu_access_mode]  # value = <cu_access_mode.shared: 1>
    def __call__(self, *args) -> run:
        ...
    @typing.overload
    def __init__(self, arg0: device, arg1: uuid, arg2: str, arg3: kernel.cu_access_mode) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: device, arg1: uuid, arg2: str) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: hw_context, arg1: str) -> None:
        ...
    def group_id(self, arg0: int) -> int:
        """
        Get the memory bank group id of an kernel argument
        """
class run:
    """
    Represents one execution of a kernel
    """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: "xrt::kernel") -> None:
        ...
    def add_callback(self, arg0: ert_cmd_state, arg1: "std::function<void (void const*, ert_cmd_state, void*)>", arg2: "capsule") -> None:
        """
        Add a callback function for run state
        """
    @typing.overload
    def set_arg(self, arg0: int, arg1: "xrt::bo") -> None:
        """
        Set a specific kernel global argument for a run
        """
    @typing.overload
    def set_arg(self, arg0: int, arg1: int) -> None:
        """
        Set a specific kernel scalar argument for this run
        """
    def start(self) -> None:
        """
        Start one execution of a run
        """
    def state(self) -> ert_cmd_state:
        """
        Check the current state of a run object
        """
    @typing.overload
    def wait(self) -> ert_cmd_state:
        """
        Wait for the run to complete
        """
    @typing.overload
    def wait(self, arg0: int) -> ert_cmd_state:
        """
        Wait for the specified milliseconds for the run to complete
        """
class uuid:
    """
    XRT UUID object to identify a compiled xclbin binary
    """
    def __init__(self, arg0: str) -> None:
        ...
    def to_string(self) -> str:
        """
        Convert XRT UUID object to string
        """
class xclBOSyncDirection:
    """
    DMA flags used with DMA API
    
    Members:
    
      XCL_BO_SYNC_BO_TO_DEVICE
    
      XCL_BO_SYNC_BO_FROM_DEVICE
    
      XCL_BO_SYNC_BO_GMIO_TO_AIE
    
      XCL_BO_SYNC_BO_AIE_TO_GMIO
    """
    XCL_BO_SYNC_BO_AIE_TO_GMIO: typing.ClassVar[xclBOSyncDirection]  # value = <xclBOSyncDirection.XCL_BO_SYNC_BO_AIE_TO_GMIO: 3>
    XCL_BO_SYNC_BO_FROM_DEVICE: typing.ClassVar[xclBOSyncDirection]  # value = <xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE: 1>
    XCL_BO_SYNC_BO_GMIO_TO_AIE: typing.ClassVar[xclBOSyncDirection]  # value = <xclBOSyncDirection.XCL_BO_SYNC_BO_GMIO_TO_AIE: 2>
    XCL_BO_SYNC_BO_TO_DEVICE: typing.ClassVar[xclBOSyncDirection]  # value = <xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE: 0>
    __members__: typing.ClassVar[dict[str, xclBOSyncDirection]]  # value = {'XCL_BO_SYNC_BO_TO_DEVICE': <xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE: 0>, 'XCL_BO_SYNC_BO_FROM_DEVICE': <xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE: 1>, 'XCL_BO_SYNC_BO_GMIO_TO_AIE': <xclBOSyncDirection.XCL_BO_SYNC_BO_GMIO_TO_AIE: 2>, 'XCL_BO_SYNC_BO_AIE_TO_GMIO': <xclBOSyncDirection.XCL_BO_SYNC_BO_AIE_TO_GMIO: 3>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class xclbin:
    """
    Represents an xclbin and provides APIs to access meta data
    """
    class xclbinip:
        def __init__(self) -> None:
            ...
        def get_name(self) -> str:
            ...
    class xclbinkernel:
        """
        Represents a kernel in an xclbin
        """
        def __init__(self) -> None:
            ...
        def get_name(self) -> str:
            """
            Get kernel name
            """
        def get_num_args(self) -> int:
            """
            Number of arguments
            """
    class xclbinmem:
        """
        Represents a physical device memory bank
        """
        def __init__(self) -> None:
            ...
        def get_base_address(self) -> int:
            """
            Get the base address of the memory bank
            """
        def get_index(self) -> int:
            """
            Get the index of the memory
            """
        def get_size_kb(self) -> int:
            """
            Get the size of the memory in KB
            """
        def get_tag(self) -> str:
            """
            Get tag name
            """
        def get_used(self) -> bool:
            """
            Get used status of the memory
            """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: str) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: "axlf") -> None:
        ...
    def get_axlf(self) -> "axlf":
        """
        Get the axlf data of the xclbin
        """
    def get_kernels(self) -> list[xclbin.xclbinkernel]:
        """
        Get list of kernels from xclbin
        """
    def get_mems(self) -> list[xclbin.xclbinmem]:
        """
        Get list of memory objects
        """
    def get_uuid(self) -> uuid:
        """
        Get the uuid of the xclbin
        """
    def get_xsa_name(self) -> str:
        """
        Get Xilinx Support Archive (XSA) name of xclbin
        """
class xclbinip_vector:
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, s: slice) -> xclbinip_vector:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> xclbin.xclbinip:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: xclbinip_vector) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[xclbin.xclbinip]:
        ...
    def __len__(self) -> int:
        ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: xclbin.xclbinip) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: xclbinip_vector) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: xclbin.xclbinip) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: xclbinip_vector) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: xclbin.xclbinip) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> xclbin.xclbinip:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> xclbin.xclbinip:
        """
        Remove and return the item at index ``i``
        """
class xclbinkernel_vector:
    def __bool__(self: list[xclbin.xclbinkernel]) -> bool:
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self: list[xclbin.xclbinkernel], arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self: list[xclbin.xclbinkernel], arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    @typing.overload
    def __getitem__(self: list[xclbin.xclbinkernel], s: slice) -> list[xclbin.xclbinkernel]:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self: list[xclbin.xclbinkernel], arg0: int) -> xclbin.xclbinkernel:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: list[xclbin.xclbinkernel]) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self: list[xclbin.xclbinkernel]) -> typing.Iterator[xclbin.xclbinkernel]:
        ...
    def __len__(self: list[xclbin.xclbinkernel]) -> int:
        ...
    @typing.overload
    def __setitem__(self: list[xclbin.xclbinkernel], arg0: int, arg1: xclbin.xclbinkernel) -> None:
        ...
    @typing.overload
    def __setitem__(self: list[xclbin.xclbinkernel], arg0: slice, arg1: list[xclbin.xclbinkernel]) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self: list[xclbin.xclbinkernel], x: xclbin.xclbinkernel) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self: list[xclbin.xclbinkernel]) -> None:
        """
        Clear the contents
        """
    @typing.overload
    def extend(self: list[xclbin.xclbinkernel], L: list[xclbin.xclbinkernel]) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self: list[xclbin.xclbinkernel], L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self: list[xclbin.xclbinkernel], i: int, x: xclbin.xclbinkernel) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self: list[xclbin.xclbinkernel]) -> xclbin.xclbinkernel:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self: list[xclbin.xclbinkernel], i: int) -> xclbin.xclbinkernel:
        """
        Remove and return the item at index ``i``
        """
class xclbinmem_vector:
    def __bool__(self: list[xclbin.xclbinmem]) -> bool:
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self: list[xclbin.xclbinmem], arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self: list[xclbin.xclbinmem], arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    @typing.overload
    def __getitem__(self: list[xclbin.xclbinmem], s: slice) -> list[xclbin.xclbinmem]:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self: list[xclbin.xclbinmem], arg0: int) -> xclbin.xclbinmem:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: list[xclbin.xclbinmem]) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self: list[xclbin.xclbinmem]) -> typing.Iterator[xclbin.xclbinmem]:
        ...
    def __len__(self: list[xclbin.xclbinmem]) -> int:
        ...
    @typing.overload
    def __setitem__(self: list[xclbin.xclbinmem], arg0: int, arg1: xclbin.xclbinmem) -> None:
        ...
    @typing.overload
    def __setitem__(self: list[xclbin.xclbinmem], arg0: slice, arg1: list[xclbin.xclbinmem]) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self: list[xclbin.xclbinmem], x: xclbin.xclbinmem) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self: list[xclbin.xclbinmem]) -> None:
        """
        Clear the contents
        """
    @typing.overload
    def extend(self: list[xclbin.xclbinmem], L: list[xclbin.xclbinmem]) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self: list[xclbin.xclbinmem], L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self: list[xclbin.xclbinmem], i: int, x: xclbin.xclbinmem) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self: list[xclbin.xclbinmem]) -> xclbin.xclbinmem:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self: list[xclbin.xclbinmem], i: int) -> xclbin.xclbinmem:
        """
        Remove and return the item at index ``i``
        """
class xrt_info_device:
    """
    Device feature and sensor information
    
    Members:
    
      bdf
    
      interface_uuid
    
      kdma
    
      max_clock_frequency_mhz
    
      m2m
    
      name
    
      nodma
    
      offline
    
      electrical
    
      thermal
    
      mechanical
    
      memory
    
      platform
    
      pcie_info
    
      host
    
      dynamic_regions
    
      vmr
    """
    __members__: typing.ClassVar[dict[str, xrt_info_device]]  # value = {'bdf': <xrt_info_device.bdf: 0>, 'interface_uuid': <xrt_info_device.interface_uuid: 1>, 'kdma': <xrt_info_device.kdma: 2>, 'max_clock_frequency_mhz': <xrt_info_device.max_clock_frequency_mhz: 3>, 'm2m': <xrt_info_device.m2m: 4>, 'name': <xrt_info_device.name: 5>, 'nodma': <xrt_info_device.nodma: 6>, 'offline': <xrt_info_device.offline: 7>, 'electrical': <xrt_info_device.electrical: 8>, 'thermal': <xrt_info_device.thermal: 9>, 'mechanical': <xrt_info_device.mechanical: 10>, 'memory': <xrt_info_device.memory: 11>, 'platform': <xrt_info_device.platform: 12>, 'pcie_info': <xrt_info_device.pcie_info: 13>, 'host': <xrt_info_device.host: 14>, 'dynamic_regions': <xrt_info_device.dynamic_regions: 17>, 'vmr': <xrt_info_device.vmr: 18>}
    bdf: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.bdf: 0>
    dynamic_regions: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.dynamic_regions: 17>
    electrical: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.electrical: 8>
    host: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.host: 14>
    interface_uuid: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.interface_uuid: 1>
    kdma: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.kdma: 2>
    m2m: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.m2m: 4>
    max_clock_frequency_mhz: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.max_clock_frequency_mhz: 3>
    mechanical: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.mechanical: 10>
    memory: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.memory: 11>
    name: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.name: 5>
    nodma: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.nodma: 6>
    offline: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.offline: 7>
    pcie_info: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.pcie_info: 13>
    platform: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.platform: 12>
    thermal: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.thermal: 9>
    vmr: typing.ClassVar[xrt_info_device]  # value = <xrt_info_device.vmr: 18>
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class xrt_msg_level:
    """
    XRT log msgs level
    
    Members:
    
      emergency
    
      alert
    
      critical
    
      error
    
      warning
    
      notice
    
      info
    
      debug
    """
    __members__: typing.ClassVar[dict[str, xrt_msg_level]]  # value = {'emergency': <xrt_msg_level.emergency: 0>, 'alert': <xrt_msg_level.alert: 1>, 'critical': <xrt_msg_level.critical: 2>, 'error': <xrt_msg_level.error: 3>, 'warning': <xrt_msg_level.warning: 4>, 'notice': <xrt_msg_level.notice: 5>, 'info': <xrt_msg_level.info: 6>, 'debug': <xrt_msg_level.debug: 7>}
    alert: typing.ClassVar[xrt_msg_level]  # value = <xrt_msg_level.alert: 1>
    critical: typing.ClassVar[xrt_msg_level]  # value = <xrt_msg_level.critical: 2>
    debug: typing.ClassVar[xrt_msg_level]  # value = <xrt_msg_level.debug: 7>
    emergency: typing.ClassVar[xrt_msg_level]  # value = <xrt_msg_level.emergency: 0>
    error: typing.ClassVar[xrt_msg_level]  # value = <xrt_msg_level.error: 3>
    info: typing.ClassVar[xrt_msg_level]  # value = <xrt_msg_level.info: 6>
    notice: typing.ClassVar[xrt_msg_level]  # value = <xrt_msg_level.notice: 5>
    warning: typing.ClassVar[xrt_msg_level]  # value = <xrt_msg_level.warning: 4>
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
def enumerate_devices() -> int:
    """
    Enumerate devices in system
    """
def log_message(arg0: xrt_msg_level, arg1: str, arg2: str) -> None:
    """
    Dispatch formatted log message
    """
XCL_BO_FLAGS_NONE: int = 0
alert: xrt_msg_level  # value = <xrt_msg_level.alert: 1>
critical: xrt_msg_level  # value = <xrt_msg_level.critical: 2>
debug: xrt_msg_level  # value = <xrt_msg_level.debug: 7>
emergency: xrt_msg_level  # value = <xrt_msg_level.emergency: 0>
error: xrt_msg_level  # value = <xrt_msg_level.error: 3>
info: xrt_msg_level  # value = <xrt_msg_level.info: 6>
notice: xrt_msg_level  # value = <xrt_msg_level.notice: 5>
warning: xrt_msg_level  # value = <xrt_msg_level.warning: 4>

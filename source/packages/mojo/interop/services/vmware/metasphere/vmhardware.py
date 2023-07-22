"""
.. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VM hardware related enumerations.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

class VmHardwareVersion:
    VMX_03 = "VMX_03"
    VMX_04 = "VMX_04"
    VMX_06 = "VMX_06"
    VMX_07 = "VMX_07"
    VMX_08 = "VMX_08"
    VMX_09 = "VMX_09"
    VMX_10 = "VMX_10"
    VMX_11 = "VMX_11"
    VMX_12 = "VMX_12"
    VMX_13 = "VMX_13"
    VMX_14 = "VMX_14"
    VMX_15 = "VMX_15"
    VMX_16 = "VMX_16"
    VMX_17 = "VMX_17"
    VMX_18 = "VMX_18"
    VMX_19 = "VMX_19"
    VMX_20 = "VMX_20"

class VmHardwareBootNetworkProtocol:
    IPV4 = "IPV4"
    IPV6 = "IPV6"

class VmHardwareBootType:
    BIOS = "BIOS"
    EFI = "EFI"

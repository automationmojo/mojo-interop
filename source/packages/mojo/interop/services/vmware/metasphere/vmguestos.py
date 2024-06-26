"""
.. module:: vmguestos
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VmGuestOS constants used when working with VM guest OS(s).

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []

class VmGuestOS:
    DOS = "DOS" # MS-DOS.
    WIN_31 = "WIN_31" # Windows 3.1
    WIN_95 = "WIN_95" # Windows 95
    WIN_98 = "WIN_98" # Windows 98
    WIN_ME = "WIN_ME" # Windows Millennium Edition
    WIN_NT = "WIN_NT" # Windows NT 4
    WIN_2000_PRO = "WIN_2000_PRO" # Windows 2000 Professional
    WIN_2000_SERV = "WIN_2000_SERV" # Windows 2000 Server
    WIN_2000_ADV_SERV = "WIN_2000_ADV_SERV" # Windows 2000 Advanced Server
    WIN_XP_HOME = "WIN_XP_HOME" # Windows XP Home Edition
    WIN_XP_PRO = "WIN_XP_PRO" # Windows XP Professional
    WIN_XP_PRO_64 = "WIN_XP_PRO_64" # Windows XP Professional Edition (64 bit)
    WIN_NET_WEB = "WIN_NET_WEB" # Windows Server 2003, Web Edition
    WIN_NET_STANDARD = "WIN_NET_STANDARD" # Windows Server 2003, Standard Edition
    WIN_NET_ENTERPRISE = "WIN_NET_ENTERPRISE" # Windows Server 2003, Enterprise Edition
    WIN_NET_DATACENTER = "WIN_NET_DATACENTER" # Windows Server 2003, Datacenter Edition
    WIN_NET_BUSINESS = "WIN_NET_BUSINESS" # Windows Small Business Server 2003
    WIN_NET_STANDARD_64 = "WIN_NET_STANDARD_64" # Windows Server 2003, Standard Edition (64 bit)
    WIN_NET_ENTERPRISE_64 = "WIN_NET_ENTERPRISE_64" # Windows Server 2003, Enterprise Edition (64 bit)
    WIN_LONGHORN = "WIN_LONGHORN" # Windows Longhorn
    WIN_LONGHORN_64 = "WIN_LONGHORN_64" # Windows Longhorn (64 bit)
    WIN_NET_DATACENTER_64 = "WIN_NET_DATACENTER_64" # Windows Server 2003, Datacenter Edition (64 bit)
    WIN_VISTA = "WIN_VISTA" # Windows Vista
    WIN_VISTA_64 = "WIN_VISTA_64" # Windows Vista (64 bit)
    WINDOWS_7 = "WINDOWS_7" # Windows 7
    WINDOWS_7_64 = "WINDOWS_7_64" # Windows 7 (64 bit)
    WINDOWS_7_SERVER_64 = "WINDOWS_7_SERVER_64" # Windows Server 2008 R2 (64 bit)
    WINDOWS_8 = "WINDOWS_8" # Windows 8
    WINDOWS_8_64 = "WINDOWS_8_64" # Windows 8 (64 bit)
    WINDOWS_8_SERVER_64 = "WINDOWS_8_SERVER_64" # Windows 8 Server (64 bit)
    WINDOWS_9 = "WINDOWS_9" # Windows 10
    WINDOWS_9_64 = "WINDOWS_9_64" # Windows 10 (64 bit)
    WINDOWS_9_SERVER_64 = "WINDOWS_9_SERVER_64" # Windows 10 Server (64 bit)
    WINDOWS_11_64 = "WINDOWS_11_64" # Windows 11 (64 bit)
    WINDOWS_12_64 = "WINDOWS_12_64" # Windows 12 (64 bit)
    WINDOWS_HYPERV = "WINDOWS_HYPERV" # Windows Hyper-V
    WINDOWS_SERVER_2019 = "WINDOWS_SERVER_2019" # Windows Server 2019
    WINDOWS_SERVER_2021 = "WINDOWS_SERVER_2021" # Windows Server 2022
    WINDOWS_SERVER_2025 = "WINDOWS_SERVER_2025" # Windows Server 2025
    FREEBSD = "FREEBSD" # FreeBSD 10 or earlier
    FREEBSD_64 = "FREEBSD_64" # FreeBSD 10 x64 or earlier
    FREEBSD_11 = "FREEBSD_11" # FreeBSD 11
    FREEBSD_12 = "FREEBSD_12" # FreeBSD 12
    FREEBSD_13 = "FREEBSD_13" # FreeBSD 13
    FREEBSD_14 = "FREEBSD_14" # FreeBSD 14 or later
    FREEBSD_11_64 = "FREEBSD_11_64" # FreeBSD 11 x64
    FREEBSD_12_64 = "FREEBSD_12_64" # FreeBSD 12 x64
    FREEBSD_13_64 = "FREEBSD_13_64" # FreeBSD 13 x64
    FREEBSD_14_64 = "FREEBSD_14_64" # FreeBSD 14 x64 or later
    REDHAT = "REDHAT" # Red Hat Linux 2.1
    RHEL_2 = "RHEL_2" # Red Hat Enterprise Linux 2
    RHEL_3 = "RHEL_3" # Red Hat Enterprise Linux 3
    RHEL_3_64 = "RHEL_3_64" # Red Hat Enterprise Linux 3 (64 bit)
    RHEL_4 = "RHEL_4" # Red Hat Enterprise Linux 4
    RHEL_4_64 = "RHEL_4_64" # Red Hat Enterprise Linux 4 (64 bit)
    RHEL_5 = "RHEL_5" # Red Hat Enterprise Linux 5
    RHEL_5_64 = "RHEL_5_64" # Red Hat Enterprise Linux 5 (64 bit)
    RHEL_6 = "RHEL_6" # Red Hat Enterprise Linux 6
    RHEL_6_64 = "RHEL_6_64" # Red Hat Enterprise Linux 6 (64 bit)
    RHEL_7 = "RHEL_7" # Red Hat Enterprise Linux 7
    RHEL_7_64 = "RHEL_7_64" # Red Hat Enterprise Linux 7 (64 bit)
    RHEL_8_64 = "RHEL_8_64" # Red Hat Enterprise Linux 8 (64 bit)
    RHEL_9_64 = "RHEL_9_64" # Red Hat Enterprise Linux 9 (64 bit)
    CENTOS = "CENTOS" # CentOS 4⁄5
    CENTOS_64 = "CENTOS_64" # CentOS 4⁄5 (64-bit)
    CENTOS_6 = "CENTOS_6" # CentOS 6
    CENTOS_6_64 = "CENTOS_6_64" # CentOS 6 (64-bit)
    CENTOS_7 = "CENTOS_7" # CentOS 7
    CENTOS_7_64 = "CENTOS_7_64" # CentOS 7 (64-bit)
    CENTOS_8_64 = "CENTOS_8_64" # CentOS 8 (64-bit)
    CENTOS_9_64 = "CENTOS_9_64" # CentOS 9 (64-bit)
    ORACLE_LINUX = "ORACLE_LINUX" # Oracle Linux 4⁄5
    ORACLE_LINUX_64 = "ORACLE_LINUX_64" # Oracle Linux 4⁄5 (64-bit)
    ORACLE_LINUX_6 = "ORACLE_LINUX_6" # Oracle Linux 6
    ORACLE_LINUX_6_64 = "ORACLE_LINUX_6_64" # Oracle Linux 6 (64-bit)
    ORACLE_LINUX_7 = "ORACLE_LINUX_7" # Oracle Linux 7
    ORACLE_LINUX_7_64 = "ORACLE_LINUX_7_64" # Oracle Linux 7 (64-bit)
    ORACLE_LINUX_8_64 = "ORACLE_LINUX_8_64" # Oracle Linux 8 (64-bit)
    ORACLE_LINUX_9_64 = "ORACLE_LINUX_9_64" # Oracle Linux 9 (64-bit)
    SUSE = "SUSE" # Suse Linux
    SUSE_64 = "SUSE_64" # Suse Linux (64 bit)
    SLES = "SLES" # Suse Linux Enterprise Server 9
    SLES_64 = "SLES_64" # Suse Linux Enterprise Server 9 (64 bit)
    SLES_10 = "SLES_10" # Suse linux Enterprise Server 10
    SLES_10_64 = "SLES_10_64" # Suse Linux Enterprise Server 10 (64 bit)
    SLES_11 = "SLES_11" # Suse linux Enterprise Server 11
    SLES_11_64 = "SLES_11_64" # Suse Linux Enterprise Server 11 (64 bit)
    SLES_12 = "SLES_12" # Suse linux Enterprise Server 12
    SLES_12_64 = "SLES_12_64" # Suse Linux Enterprise Server 12 (64 bit)
    SLES_15_64 = "SLES_15_64" # Suse Linux Enterprise Server 15 (64 bit)
    SLES_16_64 = "SLES_16_64" # Suse Linux Enterprise Server 16 (64 bit)
    NLD_9 = "NLD_9" # Novell Linux Desktop 9
    OES = "OES" # Open Enterprise Server
    SJDS = "SJDS" # Sun Java Desktop System
    MANDRAKE = "MANDRAKE" # Mandrake Linux
    MANDRIVA = "MANDRIVA" # Mandriva Linux
    MANDRIVA_64 = "MANDRIVA_64" # Mandriva Linux (64 bit)
    TURBO_LINUX = "TURBO_LINUX" # Turbolinux
    TURBO_LINUX_64 = "TURBO_LINUX_64" # Turbolinux (64 bit)
    UBUNTU = "UBUNTU" # Ubuntu Linux
    UBUNTU_64 = "UBUNTU_64" # Ubuntu Linux (64 bit)
    DEBIAN_4 = "DEBIAN_4" # Debian GNU/Linux 4
    DEBIAN_4_64 = "DEBIAN_4_64" # Debian GNU/Linux 4 (64 bit)
    DEBIAN_5 = "DEBIAN_5" # Debian GNU/Linux 5
    DEBIAN_5_64 = "DEBIAN_5_64" # Debian GNU/Linux 5 (64 bit)
    DEBIAN_6 = "DEBIAN_6" # Debian GNU/Linux 6
    DEBIAN_6_64 = "DEBIAN_6_64" # Debian GNU/Linux 6 (64 bit)
    DEBIAN_7 = "DEBIAN_7" # Debian GNU/Linux 7
    DEBIAN_7_64 = "DEBIAN_7_64" # Debian GNU/Linux 7 (64 bit)
    DEBIAN_8 = "DEBIAN_8" # Debian GNU/Linux 8
    DEBIAN_8_64 = "DEBIAN_8_64" # Debian GNU/Linux 8 (64 bit)
    DEBIAN_9 = "DEBIAN_9" # Debian GNU/Linux 9
    DEBIAN_9_64 = "DEBIAN_9_64" # Debian GNU/Linux 9 (64 bit)
    DEBIAN_10 = "DEBIAN_10" # Debian GNU/Linux 10
    DEBIAN_10_64 = "DEBIAN_10_64" # Debian GNU/Linux 10 (64 bit)
    DEBIAN_11 = "DEBIAN_11" # Debian GNU/Linux 11
    DEBIAN_11_64 = "DEBIAN_11_64" # Debian GNU/Linux 11 (64 bit)
    DEBIAN_12 = "DEBIAN_12" # Debian GNU/Linux 12
    DEBIAN_12_64 = "DEBIAN_12_64" # Debian GNU/Linux 12 (64 bit)
    ASIANUX_3 = "ASIANUX_3" # Asianux Server 3
    ASIANUX_3_64 = "ASIANUX_3_64" # Asianux Server 3 (64 bit)
    ASIANUX_4 = "ASIANUX_4" # Asianux Server 4
    ASIANUX_4_64 = "ASIANUX_4_64" # Asianux Server 4 (64 bit)
    ASIANUX_5_64 = "ASIANUX_5_64" # Asianux Server 5 (64 bit)
    ASIANUX_7_64 = "ASIANUX_7_64" # Asianux Server 7 (64 bit)
    ASIANUX_8_64 = "ASIANUX_8_64" # Asianux Server 8 (64 bit)
    ASIANUX_9_64 = "ASIANUX_9_64" # Asianux Server 9 (64 bit)
    OPENSUSE = "OPENSUSE" # OpenSUSE Linux
    OPENSUSE_64 = "OPENSUSE_64" # OpenSUSE Linux (64 bit)
    FEDORA = "FEDORA" # Fedora Linux
    FEDORA_64 = "FEDORA_64" # Fedora Linux (64 bit)
    COREOS_64 = "COREOS_64" # CoreOS Linux (64 bit)
    VMWARE_PHOTON_64 = "VMWARE_PHOTON_64" # VMware Photon (64 bit)
    OTHER_24X_LINUX = "OTHER_24X_LINUX" # Linux 2.4x Kernel
    OTHER_24X_LINUX_64 = "OTHER_24X_LINUX_64" # Linux 2.4x Kernel (64 bit)
    OTHER_26X_LINUX = "OTHER_26X_LINUX" # Linux 2.6x Kernel
    OTHER_26X_LINUX_64 = "OTHER_26X_LINUX_64" # Linux 2.6x Kernel (64 bit)
    OTHER_3X_LINUX = "OTHER_3X_LINUX" # Linux 3.x Kernel
    OTHER_3X_LINUX_64 = "OTHER_3X_LINUX_64" # Linux 3.x Kernel (64 bit)
    OTHER_4X_LINUX = "OTHER_4X_LINUX" # Linux 4.x Kernel
    OTHER_4X_LINUX_64 = "OTHER_4X_LINUX_64" # Linux 4.x Kernel (64 bit)
    OTHER_5X_LINUX = "OTHER_5X_LINUX" # Linux 5.x Kernel
    OTHER_5X_LINUX_64 = "OTHER_5X_LINUX_64" # Linux 5.x Kernel (64 bit)
    OTHER_6X_LINUX = "OTHER_6X_LINUX" # Linux 6.x Kernel
    OTHER_6X_LINUX_64 = "OTHER_6X_LINUX_64" # Linux 6.x Kernel (64 bit)
    OTHER_LINUX = "OTHER_LINUX" # Linux 2.2x Kernel
    GENERIC_LINUX = "GENERIC_LINUX" # Other Linux
    OTHER_LINUX_64 = "OTHER_LINUX_64" # Linux (64 bit)
    SOLARIS_6 = "SOLARIS_6" # Solaris 6
    SOLARIS_7 = "SOLARIS_7" # Solaris 7
    SOLARIS_8 = "SOLARIS_8" # Solaris 8
    SOLARIS_9 = "SOLARIS_9" # Solaris 9
    SOLARIS_10 = "SOLARIS_10" # Solaris 10 (32 bit)
    SOLARIS_10_64 = "SOLARIS_10_64" # Solaris 10 (64 bit)
    SOLARIS_11_64 = "SOLARIS_11_64" # Solaris 11 (64 bit)
    OS2 = "OS2" # OS/2
    ECOMSTATION = "ECOMSTATION" # eComStation 1.x
    ECOMSTATION_2 = "ECOMSTATION_2" # eComStation 2.0
    NETWARE_4 = "NETWARE_4" # Novell NetWare 4
    NETWARE_5 = "NETWARE_5" # Novell NetWare 5.1
    NETWARE_6 = "NETWARE_6" # Novell NetWare 6.x
    OPENSERVER_5 = "OPENSERVER_5" # SCO OpenServer 5
    OPENSERVER_6 = "OPENSERVER_6" # SCO OpenServer 6
    UNIXWARE_7 = "UNIXWARE_7" # SCO UnixWare 7
    DARWIN = "DARWIN" # Mac OS 10.5
    DARWIN_64 = "DARWIN_64" # Mac OS 10.5 (64 bit)
    DARWIN_10 = "DARWIN_10" # Mac OS 10.6
    DARWIN_10_64 = "DARWIN_10_64" # Mac OS 10.6 (64 bit)
    DARWIN_11 = "DARWIN_11" # Mac OS 10.7
    DARWIN_11_64 = "DARWIN_11_64" # Mac OS 10.7 (64 bit)
    DARWIN_12_64 = "DARWIN_12_64" # Mac OS 10.8 (64 bit)
    DARWIN_13_64 = "DARWIN_13_64" # Mac OS 10.9 (64 bit)
    DARWIN_14_64 = "DARWIN_14_64" # Mac OS 10.10 (64 bit)
    DARWIN_15_64 = "DARWIN_15_64" # Mac OS 10.11 (64 bit)
    DARWIN_16_64 = "DARWIN_16_64" # Mac OS 10.12 (64 bit)
    DARWIN_17_64 = "DARWIN_17_64" # Mac OS 10.13 (64 bit)
    DARWIN_18_64 = "DARWIN_18_64" # Mac OS 10.14 (64 bit)
    DARWIN_19_64 = "DARWIN_19_64" # Mac OS 10.15 (64 bit)
    DARWIN_20_64 = "DARWIN_20_64" # Mac OS 11 (64 bit)
    DARWIN_21_64 = "DARWIN_21_64" # Mac OS 12 (64 bit)
    DARWIN_22_64 = "DARWIN_22_64" # Mac OS 13 (64 bit)
    DARWIN_23_64 = "DARWIN_23_64" # Mac OS 14 (64 bit)
    VMKERNEL = "VMKERNEL" # VMware ESX 4
    VMKERNEL_5 = "VMKERNEL_5" # VMware ESX 5
    VMKERNEL_6 = "VMKERNEL_6" # VMware ESX 6
    VMKERNEL_65 = "VMKERNEL_65" # VMware ESXi 6.5 AND ESXi 6.7.
    VMKERNEL_7 = "VMKERNEL_7" # VMware ESX 7
    VMKERNEL_8 = "VMKERNEL_8" # VMware ESX 8
    AMAZONLINUX2_64 = "AMAZONLINUX2_64" # Amazon Linux 2 (64 bit)
    AMAZONLINUX3_64 = "AMAZONLINUX3_64" # Amazon Linux 3 (64 bit)
    CRXPOD_1 = "CRXPOD_1" # CRX Pod 1
    ROCKYLINUX_64 = "ROCKYLINUX_64" # Rocky Linux (64-bit)
    ALMALINUX_64 = "ALMALINUX_64" # AlmaLinux (64-bit)
    OTHER = "OTHER" # Other Operating System
    OTHER_64 = "OTHER_64" # Other Operating System (64 bit)

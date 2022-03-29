from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.unbelievable.hpe.plugins.modules.ilo_boot_order import ILOBootOrder  # type: ignore # noqa: E501


settings = {
    "BootSources": [
        {
            "BootOptionNumber": "000A",
            "BootString": "Generic USB Boot",
            "CorrelatableID": "UsbClass(0xFFFF,0xFFFF,0xFF,0xFF,0xFF)",
            "StructuredBootString": "Generic.USB.1.1",
            "UEFIDevicePath": "UsbClass(0xFFFF,0xFFFF,0xFF,0xFF,0xFF)",
        },
        {
            "BootOptionNumber": "000B",
            "BootString": "Internal SD Card 1 : Generic USB3.0-CRW",
            "CorrelatableID": "PciRoot(0x0)/Pci(0x14,0x0)/USB(0x13,0x0)",
            "StructuredBootString": "HD.SD.1.2",
            "UEFIDevicePath": "PciRoot(0x0)/Pci(0x14,0x0)/USB(0x13,0x0)",
        },
        {
            "BootOptionNumber": "000C",
            "BootString": "Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:1.746 TiB Port:1I Bay:3 Box:1",
            "CorrelatableID": "PciRoot(0x3)/Pci(0x0,0x0)/Pci(0x0,0x0)",
            "StructuredBootString": "HD.EmbRAID.1.2",
            "UEFIDevicePath": "PciRoot(0x3)/Pci(0x0,0x0)/Pci(0x0,0x0)/Scsi(0x2,0x4000)",
        },
        {
            "BootOptionNumber": "0012",
            "BootString": "Embedded FlexibleLOM 1 Port 1 : HPE Ethernet 10Gb 2-Port 535FLR-T Adapter - NIC (PXE IPv4)",
            "CorrelatableID": "PciRoot(0x3)/Pci(0x2,0x0)/Pci(0x0,0x0)",
            "StructuredBootString": "NIC.FlexLOM.1.1.IPv4",
            "UEFIDevicePath": "PciRoot(0x3)/Pci(0x2,0x0)/Pci(0x0,0x0)/MAC(F40343C5F690,0x1)/IPv4(0.0.0.0,0x0,DHCP,0.0.0.0,0.0.0.0,0.0.0.0)",  # noqa: E501
        },
        {
            "BootOptionNumber": "0010",
            "BootString": "Embedded FlexibleLOM 1 Port 1 : HPE Ethernet 10Gb 2-Port 535FLR-T Adapter - NIC (HTTP(S) IPv4)",  # noqa: E501
            "CorrelatableID": "PciRoot(0x3)/Pci(0x2,0x0)/Pci(0x0,0x0)",
            "StructuredBootString": "NIC.FlexLOM.1.1.Httpv4",
            "UEFIDevicePath": "PciRoot(0x3)/Pci(0x2,0x0)/Pci(0x0,0x0)/MAC(F40343C5F690,0x1)/IPv4(0.0.0.0,0x0,DHCP,0.0.0.0,0.0.0.0,0.0.0.0)/Uri()",  # noqa: E501
        },
        {
            "BootOptionNumber": "000F",
            "BootString": "iLO Virtual USB 4 : iLO Virtual USB Key",
            "CorrelatableID": "PciRoot(0x0)/Pci(0x1C,0x4)/Pci(0x0,0x4)/USB(0x2,0x0)",
            "StructuredBootString": "FD.Virtual.4.1",
            "UEFIDevicePath": "PciRoot(0x0)/Pci(0x1C,0x4)/Pci(0x0,0x4)/USB(0x2,0x0)",
        },
        {
            "BootOptionNumber": "000D",
            "BootString": "Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:1.746 TiB Port:1I Bay:4 Box:1",
            "CorrelatableID": "PciRoot(0x3)/Pci(0x0,0x0)/Pci(0x0,0x0)",
            "StructuredBootString": "HD.EmbRAID.1.3",
            "UEFIDevicePath": "PciRoot(0x3)/Pci(0x0,0x0)/Pci(0x0,0x0)/Scsi(0x3,0x4000)",
        },
        {
            "BootOptionNumber": "000E",
            "BootString": "Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - 447.1 GiB, RAID1 Logical Drive 1(Target:0, Lun:0)",  # noqa: E501
            "CorrelatableID": "PciRoot(0x3)/Pci(0x0,0x0)/Pci(0x0,0x0)",
            "StructuredBootString": "HD.EmbRAID.1.4",
            "UEFIDevicePath": "PciRoot(0x3)/Pci(0x0,0x0)/Pci(0x0,0x0)/Scsi(0x0,0x0)",
        },
    ]
}


@pytest.mark.parametrize(
    "boot_sources, patterns, expected_result",
    [
        (
            list(settings["BootSources"]),
            [
                ".*Generic USB Boot.*",
                ".*Internal SD Card 1 :.*",
                ".*Logical Drive 1\\(.*",
                ".*NIC \\(PXE IPv4\\).*",
                ".*NIC \\(HTTP\\(S\\) IPv4.*",
            ],
            [
                "Generic.USB.1.1",
                "HD.SD.1.2",
                "HD.EmbRAID.1.4",
                "NIC.FlexLOM.1.1.IPv4",
                "NIC.FlexLOM.1.1.Httpv4",
                "HD.EmbRAID.1.2",
                "FD.Virtual.4.1",
                "HD.EmbRAID.1.3",
            ],
        ),
        (
            list(settings["BootSources"]),
            [
                ".*NIC \\(HTTP\\(S\\) IPv4.*",
                ".*NIC \\(PXE IPv4\\).*",
                ".*Generic USB Boot.*",
                ".*Internal SD Card 1 :.*",
                ".*Logical Drive 1\\(.*",
            ],
            [
                "NIC.FlexLOM.1.1.Httpv4",
                "NIC.FlexLOM.1.1.IPv4",
                "Generic.USB.1.1",
                "HD.SD.1.2",
                "HD.EmbRAID.1.4",
                "HD.EmbRAID.1.2",
                "FD.Virtual.4.1",
                "HD.EmbRAID.1.3",
            ],
        ),
    ],
)
def test_compute_new_order(boot_sources, patterns, expected_result):
    result = ILOBootOrder.compute_new_order(boot_sources, patterns)
    assert expected_result == result

{
    "apiVersion": "2025-04-01",
    "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/RG-CU-CORPAPPS-MIGRATIONTEST-DEV/providers/Microsoft.Compute/virtualMachines/VMCUWINWEBD10",
    "name": "VMCUWINWEBD10",
    "type": "microsoft.compute/virtualmachines",
    "location": "centralus",
    "tags": {
        "Application": "Movit",
        "BillTo": "200000060548",
        "BusinessCriticality": "Tier 4",
        "ContactEmail": "cloudplatform@dteenergy.com",
        "DataClassification": "Internal",
        "ItAppOwnerEmail": "cloudplatform@dteenergy.com",
        "Environment": "Dev",
        "Portfolio": "CorpApps",
        "Project": "VVMWare",
        "onprem_name": "dca-tst1856"
    },
    "properties": {
        "hardwareProfile": {
            "vmSize": "Standard_D2s_v5"
        },
        "provisioningState": "Updating",
        "vmId": "62db196f-0a46-4687-8d8b-eebae16a23c3",
        "storageProfile": {
            "osDisk": {
                "osType": "Windows",
                "name": "VMCUWINWEBD10-OSdisk-00",
                "createOption": "Attach",
                "caching": "ReadWrite",
                "managedDisk": {
                    "storageAccountType": "Standard_LRS",
                    "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/disks/VMCUWINWEBD10-OSdisk-00"
                },
                "deleteOption": "Detach",
                "diskSizeGB": 100
            },
            "dataDisks": [
                {
                    "lun": 0,
                    "name": "VMCUWINWEBD10-datadisk-01",
                    "createOption": "Attach",
                    "caching": "None",
                    "managedDisk": {
                        "storageAccountType": "Standard_LRS",
                        "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/disks/VMCUWINWEBD10-datadisk-01"
                    },
                    "deleteOption": "Detach",
                    "diskSizeGB": 70,
                    "toBeDetached": false
                }
            ]
        },
        "networkProfile": {
            "networkInterfaces": [
                {
                    "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Network/networkInterfaces/nic-VMCUWINWEBD10-00",
                    "properties": {
                        "primary": true
                    }
                }
            ]
        },
        "diagnosticsProfile": {
            "bootDiagnostics": {
                "enabled": true
            }
        },
        "licenseType": "Windows_Server",
        "timeCreated": "2026-03-03T12:54:41.496Z"
    },
    "etag": "\"2\""
}
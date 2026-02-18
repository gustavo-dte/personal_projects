{
    "apiVersion": "2025-04-01",
    "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/virtualMachines/vmcuwinwebd01",
    "name": "vmcuwinwebd01",
    "type": "microsoft.compute/virtualmachines",
    "location": "centralus",
    "tags": {
        "Application": "CorpApps",
        "BillTo": "100000069697",
        "BusinessCriticality": "Tier 4",
        "CreatedBy": "Cloud Platform Team",
        "DataClassification": "Internal",
        "Environment": "Development",
        "ItAppOwnerEmail": "cloudplatform@dteenergy.com",
        "Portfolio": "CCOE"
    },
    "properties": {
        "hardwareProfile": {
            "vmSize": "Standard_D2s_v5"
        },
        "provisioningState": "Succeeded",
        "vmId": "8d821b70-45d6-400e-8de1-2b9edfb9112b",
        "virtualMachineScaleSet": {
            "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/virtualMachineScaleSets/vmss-vmcuwinwebd01"
        },
        "storageProfile": {
            "osDisk": {
                "osType": "Windows",
                "name": "vmcuwinwebd01-OSdisk-00",
                "createOption": "Attach",
                "caching": "ReadWrite",
                "managedDisk": {
                    "storageAccountType": "Standard_LRS",
                    "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/disks/vmcuwinwebd01-OSdisk-00"
                },
                "deleteOption": "Detach",
                "diskSizeGB": 100
            },
            "dataDisks": [
                {
                    "lun": 0,
                    "name": "vmcuwinwebd01-datadisk-01",
                    "createOption": "Attach",
                    "caching": "None",
                    "managedDisk": {
                        "storageAccountType": "Standard_LRS",
                        "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/disks/vmcuwinwebd01-datadisk-01"
                    },
                    "deleteOption": "Detach",
                    "diskSizeGB": 50,
                    "toBeDetached": false
                }
            ]
        },
        "networkProfile": {
            "networkInterfaces": [
                {
                    "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Network/networkInterfaces/nic-vmcuwinwebd01-00",
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
        "timeCreated": "2026-02-04T20:35:49.833Z"
    },
    "resources": [
        {
            "name": "AzureMonitorWindowsAgent",
            "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/virtualMachines/vmcuwinwebd01/extensions/AzureMonitorWindowsAgent",
            "type": "Microsoft.Compute/virtualMachines/extensions",
            "location": "centralus",
            "tags": {},
            "properties": {
                "autoUpgradeMinorVersion": true,
                "provisioningState": "Succeeded",
                "enableAutomaticUpgrade": false,
                "suppressFailures": false,
                "publisher": "Microsoft.Azure.Monitor",
                "type": "AzureMonitorWindowsAgent",
                "typeHandlerVersion": "1.0"
            }
        },
        {
            "name": "DependencyAgentWindows",
            "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/virtualMachines/vmcuwinwebd01/extensions/DependencyAgentWindows",
            "type": "Microsoft.Compute/virtualMachines/extensions",
            "location": "centralus",
            "tags": {},
            "properties": {
                "autoUpgradeMinorVersion": true,
                "provisioningState": "Succeeded",
                "enableAutomaticUpgrade": false,
                "suppressFailures": false,
                "publisher": "Microsoft.Azure.Monitoring.DependencyAgent",
                "type": "DependencyAgentWindows",
                "typeHandlerVersion": "9.10"
            }
        },
        {
            "name": "MDE.Windows",
            "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/virtualMachines/vmcuwinwebd01/extensions/MDE.Windows",
            "type": "Microsoft.Compute/virtualMachines/extensions",
            "location": "centralus",
            "properties": {
                "autoUpgradeMinorVersion": true,
                "forceUpdateTag": "06f93fe7-9517-4a5f-a568-bc06c1a20a10",
                "provisioningState": "Succeeded",
                "publisher": "Microsoft.Azure.AzureDefenderForServers",
                "type": "MDE.Windows",
                "typeHandlerVersion": "1.0",
                "settings": {
                    "azureResourceId": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/RG-CU-CORPAPPS-MIGRATIONTEST-DEV/providers/Microsoft.Compute/virtualMachines/vmcuwinwebd01",
                    "forceReOnboarding": false,
                    "vNextEnabled": true,
                    "autoUpdate": true
                }
            }
        }
    ],
    "etag": "\"13\""
}
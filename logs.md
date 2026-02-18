{
    "apiVersion": "2022-11-01-preview",
    "id": "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Maintenance/maintenanceConfigurations/weekly-sunday-2am",
    "name": "weekly-sunday-2am",
    "type": "microsoft.maintenance/maintenanceconfigurations",
    "location": "centralus",
    "tags": {
        "Application": "CorpApps",
        "BillTo": "100000069697",
        "BusinessCriticality": "Tier 4",
        "CreatedBy": "Cloud Platform Team",
        "DataClassification": "Internal",
        "Description": "Web server - patched weekly on Sunday at 2 AM",
        "Environment": "Development",
        "ItAppOwnerEmail": "cloudplatform@dteenergy.com",
        "Portfolio": "CCOE",
        "Purpose": "VM Patching"
    },
    "properties": {
        "namespace": "Microsoft.Maintenance",
        "extensionProperties": {
            "InGuestPatchMode": "User"
        },
        "maintenanceScope": "InGuestPatch",
        "maintenanceWindow": {
            "startDateTime": "2026-01-01 02:00",
            "duration": "03:00",
            "timeZone": "Central Standard Time",
            "recurEvery": "Week Sunday"
        },
        "visibility": "Custom",
        "installPatches": {
            "rebootSetting": "IfRequired",
            "windowsParameters": {
                "kbNumbersToExclude": [],
                "kbNumbersToInclude": [],
                "classificationsToInclude": [
                    "Critical",
                    "Security",
                    "UpdateRollup",
                    "FeaturePack",
                    "ServicePack",
                    "Definition",
                    "Tools",
                    "Updates"
                ]
            }
        },
        "configurationType": "Regular"
    }
}
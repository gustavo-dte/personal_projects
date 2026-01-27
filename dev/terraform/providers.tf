terraform {
  required_version = ">=1.8.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>4.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "1.15.0"
    }
    github = {
      source  = "integrations/github"
      version = "6.4.0"
    }
    infoblox = {
      source  = "infobloxopen/infoblox"
      version = "2.6.0"
    }
  }

  cloud {
    organization = "DTE-Cloud-Platform"
    workspaces {
      name = "subscription-app-pattern-corpapps-dev"
    }
  }
}

provider "azurerm" {
  use_cli             = false
  storage_use_azuread = true
  features {}
}

provider "azurerm" {
  alias           = "vmimage"
  subscription_id = "13e903eb-325f-4183-b412-5fa8b77bbaad"
  features {}
}

// GitHub provider is required to create VNET Connection to VHUB
provider "github" {
  token = var.github_token
  owner = var.github_organization
}

// Infoblox provider is required to work with IPAM
provider "infoblox" {
  server   = var.infoblox_server
  username = var.infoblox_username
  password = var.infoblox_password
}

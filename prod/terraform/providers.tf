terraform {
  required_version = ">=1.8.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    github = {
      source  = "integrations/github"
      version = "6.2.1"
    }
    infoblox = {
      source  = "infobloxopen/infoblox"
      version = "2.6.0"
    }
  }

  cloud {
    organization = "DTE-Cloud-Platform"
    workspaces {
      name = "subscription-app-pattern-corpapps-prod"
    }
  }
}

provider "azurerm" {
  use_cli             = false
  storage_use_azuread = true
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

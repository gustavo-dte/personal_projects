terraform {
  required_version = ">= 1.8.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>4.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "3.2.3"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }
}

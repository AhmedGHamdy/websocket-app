terraform {
  required_version = ">= 0.13"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}

# Generate a random suffix for uniqueness
resource "random_integer" "suffix" {
  min = 10000
  max = 99999
}

# ---------------------------
# Resource Group
# ---------------------------
resource "azurerm_resource_group" "rg" {
  name     = "websock"
  location = "westeurope"
}

# ---------------------------
# Application Insights
# ---------------------------
resource "azurerm_application_insights" "ai" {
  name                = "websocket-app-ai-${random_integer.suffix.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
}

# ---------------------------
# Key Vault and Secret
# ---------------------------
resource "azurerm_key_vault" "kv" {
  name                     = "kv-websocket-app-${random_integer.suffix.result}"
  location                 = azurerm_resource_group.rg.location
  resource_group_name      = azurerm_resource_group.rg.name
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "standard"
  purge_protection_enabled = true

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete",
    ]
  }
}

resource "azurerm_key_vault_secret" "ai_conn" {
  name         = "appinsights-connection-string"
  value        = azurerm_application_insights.ai.connection_string
  key_vault_id = azurerm_key_vault.kv.id
}

data "azurerm_key_vault_secret" "ai_conn" {
  name         = azurerm_key_vault_secret.ai_conn.name
  key_vault_id = azurerm_key_vault.kv.id
}

# ---------------------------
# Azure Container Registry (ACR)
# ---------------------------
resource "azurerm_container_registry" "acr" {
  name                = "acrwebsocketapp"  # <CHANGE_ME: ACR name if needed>
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

# ---------------------------
# Service Plan (Linux)
# ---------------------------
resource "azurerm_service_plan" "asp" {
  name                = "asp-websocket-app-${random_integer.suffix.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "B1"
}

# ---------------------------
# Linux Web App (for Docker container)
# ---------------------------
resource "azurerm_linux_web_app" "app" {
  name                = "websocket-app-${random_integer.suffix.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    websockets_enabled = true
  }

  app_settings = {
    "DOCKER_CUSTOM_IMAGE_NAME"       = "${azurerm_container_registry.acr.login_server}/websocket-app:latest"
    "WEBSITES_PORT"                  = "8080"
    "DOCKER_REGISTRY_SERVER_URL"     = "https://${azurerm_container_registry.acr.login_server}"
    "DOCKER_REGISTRY_SERVER_USERNAME"= azurerm_container_registry.acr.admin_username
    "DOCKER_REGISTRY_SERVER_PASSWORD"= azurerm_container_registry.acr.admin_password
    "APPINSIGHTS_CONNECTION_STRING"  = data.azurerm_key_vault_secret.ai_conn.value
  }
}

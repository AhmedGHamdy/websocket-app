variable "resource_group_name" {
  description = "Name of the resource group."
  type        = string
  default     = "websock"   # e.g., "rg-websocket-app"
}

variable "location" {
  description = "Azure region for deployment."
  type        = string
  default     = "westeurope"              # e.g., "westeurope"
}

variable "acr_name" {
  description = "Name of the Azure Container Registry."
  type        = string
  default     = "acrwebsocketapp"              # e.g., "acrwebsocketapp"
}

variable "repository_name" {
  description = "Repository name in ACR containing the Docker image."
  type        = string
  default     = "websocket-app"       # e.g., "websocket-app"
}

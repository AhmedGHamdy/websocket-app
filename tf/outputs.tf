output "app_service_url" {
  value       = azurerm_linux_web_app.app.default_hostname
  description = "The URL of the deployed Linux Web App."
}

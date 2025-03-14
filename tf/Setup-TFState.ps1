# Setup-TFState.ps1
# This script creates the resource group, storage account, and blob container for Terraform state.
# Change the values marked as <CHANGE_ME> to match your environment.

# Check if the user is logged in. If not, log in.
try {
    az account show > $null 2>&1
}
catch {
    Write-Host "Not logged in. Please log in to your Azure account."
    az login
}

# Variables - update these as needed
$location = "westeurope"    # e.g., "eastus"
$tfStateRg = "websock"  # e.g., "tfstate-rg"

# If the resource group for Terraform state does not exist, create one.
$rgExists = az group exists --name $tfStateRg | ConvertFrom-Json
if (-not $rgExists) {
    Write-Host "Creating Resource Group: $tfStateRg in $location"
    az group create --name $tfStateRg --location $location | Out-Null
} else {
    Write-Host "Resource Group '$tfStateRg' already exists."
}

# Generate a unique storage account name (3-24 lowercase letters and numbers)
$chars = "abcdefghijklmnopqrstuvwxyz0123456789"
$randomStr = -join ((1..8) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
$storageAccountName = "tfstate$randomStr"  # e.g., "tfstateabc123xy"

# Blob container name for Terraform state (no uppercase, no special characters)
$containerName = "tfstate-container"  # e.g., "tfstate"

Write-Host "Creating Storage Account: $storageAccountName in Resource Group: $tfStateRg"
az storage account create `
  --name $storageAccountName `
  --resource-group $tfStateRg `
  --location $location `
  --sku Standard_LRS | Out-Null

Write-Host "Creating Blob Container: $containerName in Storage Account: $storageAccountName"
az storage container create `
  --name $containerName `
  --account-name $storageAccountName | Out-Null

Write-Host "Setup complete!"
Write-Host "Resource Group: $tfStateRg"
Write-Host "Storage Account: $storageAccountName"
Write-Host "Blob Container: $containerName"

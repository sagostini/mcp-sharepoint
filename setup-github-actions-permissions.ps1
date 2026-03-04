# Setup GitHub Actions service principal permissions for Azure deployment
# This script grants the necessary permissions for the GitHub Actions workflow to deploy to Azure

Write-Host "=== GitHub Actions Azure Permissions Setup ===" -ForegroundColor Cyan
Write-Host ""

# Prompt for Client ID
Write-Host "Go to GitHub Secrets: https://github.com/sagostini/mcp-sharepoint/settings/secrets/actions" -ForegroundColor Yellow
Write-Host "Find the secret named: AZUREAPPSERVICE_CLIENTID_90A8D55B7E24466DB05B8824953FE721" -ForegroundColor Yellow
Write-Host ""
$clientId = Read-Host "Enter the Client ID (Application ID)"

if ([string]::IsNullOrWhiteSpace($clientId)) {
    Write-Host "Error: Client ID is required" -ForegroundColor Red
    exit 1
}

# Configuration
$subscriptionId = "f3894b7b-cb77-4af9-ae6d-5d6310f75099"
$acrName = "cluxitregistry"
$resourceGroup = "AI"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  Subscription ID: $subscriptionId"
Write-Host "  ACR Name: $acrName"
Write-Host "  Resource Group: $resourceGroup"
Write-Host "  Client ID: $clientId"
Write-Host ""

# Verify Azure login
Write-Host "Verifying Azure login..." -ForegroundColor Cyan
$currentAccount = az account show 2>$null
if (!$?) {
    Write-Host "Error: Not logged in to Azure. Run 'az login' first." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Logged in to Azure" -ForegroundColor Green
Write-Host ""

# Grant Contributor role on subscription
Write-Host "Granting Contributor role on subscription..." -ForegroundColor Cyan
az role assignment create `
    --assignee $clientId `
    --role "Contributor" `
    --scope "/subscriptions/$subscriptionId" `
    2>$null

if ($?) {
    Write-Host "✓ Contributor role granted on subscription" -ForegroundColor Green
} else {
    Write-Host "⚠ Role may already exist or permission denied" -ForegroundColor Yellow
}
Write-Host ""

# Get ACR resource ID
Write-Host "Getting ACR resource ID..." -ForegroundColor Cyan
$acrId = az acr show --name $acrName --resource-group $resourceGroup --query id -o tsv 2>$null
if (!$?) {
    Write-Host "Error: Could not find ACR '$acrName' in resource group '$resourceGroup'" -ForegroundColor Red
    exit 1
}
Write-Host "✓ ACR found: $acrId" -ForegroundColor Green
Write-Host ""

# Grant AcrPush role
Write-Host "Granting AcrPush role on ACR..." -ForegroundColor Cyan
az role assignment create `
    --assignee $clientId `
    --role "AcrPush" `
    --scope $acrId `
    2>$null

if ($?) {
    Write-Host "✓ AcrPush role granted on ACR" -ForegroundColor Green
} else {
    Write-Host "⚠ Role may already exist or permission denied" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Verify the federated credential in Azure Portal:"
Write-Host "   - Go to Microsoft Entra ID → App Registrations"
Write-Host "   - Find your app (Client ID: $clientId)"
Write-Host "   - Check 'Certificates & secrets' → 'Federated credentials'"
Write-Host "   - Should have: Subject = repo:sagostini/mcp-sharepoint:ref:refs/heads/main"
Write-Host ""
Write-Host "2. Test the GitHub Actions workflow:"
Write-Host "   - Go to: https://github.com/sagostini/mcp-sharepoint/actions"
Write-Host "   - Click 'Re-run all jobs' on the failed workflow"
Write-Host ""

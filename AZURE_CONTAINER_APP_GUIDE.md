# Azure Container App Deployment Guide

## Prerequisites

1. **Azure Container Registry (ACR)**: Create one if you don't have it
2. **Azure Container App**: Create a container app instance
3. **GitHub Secrets**: Configure in your repository

## Step 1: Create Azure Container Registry

```bash
# Login to Azure
az login

# Create resource group (if needed)
az group create --name cluxit-rg --location westeurope

# Create Azure Container Registry
az acr create --resource-group cluxit-rg \
  --name cluxitregistry --sku Basic
```

## Step 2: Create Azure Container App

```bash
# Create Container Apps environment
az containerapp env create \
  --name cluxit-env \
  --resource-group cluxit-rg \
  --location westeurope

# Create the Container App
az containerapp create \
  --name cluxit-mcp-sharepoint \
  --resource-group cluxit-rg \
  --environment cluxit-env \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi

# Enable ACR integration
az containerapp registry set \
  --name cluxit-mcp-sharepoint \
  --resource-group cluxit-rg \
  --server cluxitregistry.azurecr.io \
  --identity system
```

## Step 3: Configure Environment Variables

Set the required SharePoint credentials in Azure Container App:

```bash
az containerapp update \
  --name cluxit-mcp-sharepoint \
  --resource-group cluxit-rg \
  --set-env-vars \
    SHAREPOINT_SITE_URL=https://yourcompany.sharepoint.com/sites/yoursite \
    SHAREPOINT_CLIENT_ID=your-client-id \
    SHAREPOINT_CLIENT_SECRET=your-client-secret \
    SHAREPOINT_TENANT_ID=your-tenant-id
```

Or set them via Azure Portal:
1. Go to your Container App
2. Navigate to **Settings** > **Environment variables**
3. Add:
   - `SHAREPOINT_SITE_URL`
   - `SHAREPOINT_CLIENT_ID`
   - `SHAREPOINT_CLIENT_SECRET`
   - `SHAREPOINT_TENANT_ID`

## Step 4: Update GitHub Workflow Variables

In the workflow file [`.github/workflows/main_cluxit-mcp-sharepoint.yml`](.github/workflows/main_cluxit-mcp-sharepoint.yml), update these values:

```yaml
env:
  AZURE_CONTAINER_REGISTRY: cluxitregistry  # Your ACR name (without .azurecr.io)
  CONTAINER_APP_NAME: cluxit-mcp-sharepoint # Your Container App name
  RESOURCE_GROUP: cluxit-rg                  # Your Resource Group name
  IMAGE_NAME: mcp-sharepoint                 # Docker image name
```

## Step 5: GitHub Actions Secrets

Your GitHub secrets should already be configured:
- ✅ `AZUREAPPSERVICE_CLIENTID_90A8D55B7E24466DB05B8824953FE721`
- ✅ `AZUREAPPSERVICE_TENANTID_61F9C60146D941539ADA0CC9AE9C1307`
- ✅ `AZUREAPPSERVICE_SUBSCRIPTIONID_E9247FB4918344FD9585E39094240E7A`

## Step 6: Deploy

Push to the `main` branch or trigger the workflow manually:

```bash
git add .
git commit -m "Configure Azure Container App deployment"
git push origin main
```

## Testing the Deployment

Once deployed, test the endpoints:

```bash
# Get the Container App URL
az containerapp show \
  --name cluxit-mcp-sharepoint \
  --resource-group cluxit-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv

# Test health endpoint
curl https://cluxit-mcp-sharepoint.your-region.azurecontainerapps.io/health

# Check configuration status
curl https://cluxit-mcp-sharepoint.your-region.azurecontainerapps.io/config

# List available tools
curl https://cluxit-mcp-sharepoint.your-region.azurecontainerapps.io/tools
```

## Monitoring

View logs in Azure Portal or via CLI:

```bash
# Stream logs
az containerapp logs show \
  --name cluxit-mcp-sharepoint \
  --resource-group cluxit-rg \
  --follow

# View metrics
az monitor metrics list \
  --resource /subscriptions/{subscription-id}/resourceGroups/cluxit-rg/providers/Microsoft.App/containerApps/cluxit-mcp-sharepoint
```

## Scaling Configuration

```bash
# Update scaling rules
az containerapp update \
  --name cluxit-mcp-sharepoint \
  --resource-group cluxit-rg \
  --min-replicas 1 \
  --max-replicas 5 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50
```

## Cost Optimization

- Use **Consumption plan** for variable workloads
- Set appropriate **min/max replicas**
- Consider scaling to zero when not in use

## Troubleshooting

### Container fails to start
```bash
# Check container logs
az containerapp logs show --name cluxit-mcp-sharepoint --resource-group cluxit-rg --tail 100

# Check revision status
az containerapp revision list --name cluxit-mcp-sharepoint --resource-group cluxit-rg
```

### ACR authentication issues
```bash
# Ensure managed identity has ACR pull permission
az role assignment create \
  --assignee $(az containerapp show --name cluxit-mcp-sharepoint --resource-group cluxit-rg --query identity.principalId -o tsv) \
  --role AcrPull \
  --scope $(az acr show --name cluxitregistry --query id -o tsv)
```

### Environment variables not set
- Verify in Azure Portal under Container App > Settings > Environment variables
- Restart the container app after changing environment variables

## Support

For issues with:
- **Azure resources**: Check Azure Portal diagnostics
- **GitHub Actions**: Review workflow run logs
- **SharePoint connectivity**: Verify credentials and permissions

"""
HTTP wrapper for SharePoint MCP Server
Exposes the MCP server functionality via HTTP endpoints for Azure Container App deployment
"""
import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(
    title="SharePoint MCP Server HTTP Wrapper",
    description="HTTP API wrapper for SharePoint MCP Server",
    version="0.1.7"
)

class MCPRequest(BaseModel):
    """Request model for MCP operations"""
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    """Response model for MCP operations"""
    success: bool
    data: Any = None
    error: str = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SharePoint MCP Server",
        "version": "0.1.7",
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp (POST)",
            "tools": "/tools (GET)"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint for Azure Container App"""
    return {"status": "healthy", "service": "mcp-sharepoint"}

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "List_SharePoint_Folders",
                "description": "Lists all folders in a specified directory or root"
            },
            {
                "name": "Create_Folder",
                "description": "Creates new folders in specified directories"
            },
            {
                "name": "Delete_Folder",
                "description": "Safely deletes empty folders from SharePoint"
            },
            {
                "name": "Get_SharePoint_Tree",
                "description": "Gets a recursive tree view of SharePoint folder structure"
            },
            {
                "name": "List_SharePoint_Documents",
                "description": "Fetches all documents within a specified folder with metadata"
            },
            {
                "name": "Get_Document_Content",
                "description": "Retrieves and processes document content"
            },
            {
                "name": "Upload_Document",
                "description": "Uploads new documents to specified folders"
            },
            {
                "name": "Upload_Document_From_Path",
                "description": "Direct file upload from local filesystem for large files"
            },
            {
                "name": "Update_Document",
                "description": "Updates content of existing documents"
            },
            {
                "name": "Delete_Document",
                "description": "Removes documents from specified folders"
            }
        ]
    }

@app.post("/mcp")
async def execute_mcp_command(request: MCPRequest):
    """
    Execute MCP command via subprocess
    This is a simplified wrapper - for production use, consider implementing direct tool calls
    """
    try:
        # Prepare the MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": request.method,
            "params": request.params
        }
        
        # Note: This is a simplified implementation
        # In production, you should implement direct tool imports and calls
        return MCPResponse(
            success=True,
            data={"message": "MCP command received", "request": mcp_request}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
async def get_config():
    """Get configuration status"""
    config = {
        "sharepoint_site_url": "configured" if os.getenv("SHAREPOINT_SITE_URL") else "missing",
        "sharepoint_client_id": "configured" if os.getenv("SHAREPOINT_CLIENT_ID") else "missing",
        "sharepoint_client_secret": "configured" if os.getenv("SHAREPOINT_CLIENT_SECRET") else "missing",
        "sharepoint_tenant_id": "configured" if os.getenv("SHAREPOINT_TENANT_ID") else "missing"
    }
    
    all_configured = all(v == "configured" for v in config.values())
    
    return {
        "status": "ready" if all_configured else "configuration_needed",
        "config": config,
        "message": "All required environment variables configured" if all_configured 
                  else "Some environment variables are missing. Configure them in Azure Container App settings."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

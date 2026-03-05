import os, logging, tempfile, time, functools
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

# Configure logging with a safe log file path
log_dir = Path(tempfile.gettempdir()) / 'mcp_sharepoint'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'mcp_sharepoint.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger('mcp_sharepoint')

# Load environment variables
load_dotenv()

# Configuration
SHP_ID_APP = os.getenv('SHP_ID_APP')
SHP_ID_APP_SECRET = os.getenv('SHP_ID_APP_SECRET')
SHP_SITE_URL = os.getenv('SHP_SITE_URL')
SHP_DOC_LIBRARY = os.getenv('SHP_DOC_LIBRARY', 'Shared Documents/mcp_server')
SHP_TENANT_ID = os.getenv('SHP_TENANT_ID')

if not SHP_SITE_URL:
    logger.error("SHP_SITE_URL environment variable not set.")
    raise ValueError("SHP_SITE_URL environment variable not set.")
if not SHP_ID_APP:
    logger.error("SHP_ID_APP environment variable not set.")
    raise ValueError("SHP_ID_APP environment variable not set.")
if not SHP_ID_APP_SECRET:
    logger.error("SHP_ID_APP_SECRET environment variable not set.")
    raise ValueError("SHP_ID_APP_SECRET environment variable not set.")

# Initialize MCP server
mcp = FastMCP(
    name="mcp_sharepoint",
    instructions=f"This server provides tools to interact with SharePoint documents and folders in {SHP_DOC_LIBRARY}"
)

# SharePoint context management
def get_sp_context():
    """Get a fresh SharePoint context"""
    credentials = ClientCredential(SHP_ID_APP, SHP_ID_APP_SECRET)
    return ClientContext(SHP_SITE_URL).with_credentials(credentials)

# Global context (can be refreshed)
sp_context = get_sp_context()

def retry_on_connection_error(max_retries=3, delay=1.0):
    """Decorator to retry SharePoint operations on connection errors"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global sp_context
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionResetError, ConnectionError, OSError) as e:
                    last_exception = e
                    logger.warning(f"Connection error on attempt {attempt + 1}/{max_retries}: {e}")
                    
                    if attempt < max_retries - 1:
                        # Refresh context and retry
                        sp_context = get_sp_context()
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Refreshing connection and retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
                        raise last_exception
                except Exception as e:
                    # For non-connection errors, check if it's a 403 or similar
                    error_str = str(e)
                    if "403" in error_str or "Forbidden" in error_str or "401" in error_str:
                        last_exception = e
                        logger.warning(f"Auth error on attempt {attempt + 1}/{max_retries}: {e}")
                        
                        if attempt < max_retries - 1:
                            sp_context = get_sp_context()
                            wait_time = delay * (2 ** attempt)
                            logger.info(f"Refreshing authentication and retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"All {max_retries} attempts failed")
                            raise
                    else:
                        # Other errors, don't retry
                        raise
            
            raise last_exception
        return wrapper
    return decorator
from app.core.config import app_config
from app.utils.http_client.base_class import HttpClient   

# Base Url
ether_scan_url = app_config.etherscan_base_url

# Singleton http client
ether_scan_client = HttpClient(name="ether_scan_api", base_url=ether_scan_url)

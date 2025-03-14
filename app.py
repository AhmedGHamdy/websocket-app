import asyncio
import websockets
import json
import random
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from aiohttp import web

# ======================
# Configuration Setup
# ======================

# Azure Application Insights Configuration
connection_string = os.getenv('APPINSIGHTS_CONNECTION_STRING')
if not connection_string:
    raise ValueError("Application Insights connection string not configured")

# Azure required port configuration
SERVER_PORT = int(os.getenv("PORT", "8080"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string=connection_string))
logger.addHandler(logging.StreamHandler())  # For Azure console logging

# Application Constants
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]
PING_INTERVAL = 10  # Seconds between keep-alive pings

# ======================
# Web Server Setup (for Azure health checks)
# ======================

async def health_check(request):
    """HTTP endpoint for Azure health checks"""
    return web.Response(text="OK")

# ======================
# WebSocket Server Logic
# ======================

async def stock_price_stream(websocket):
    """Main WebSocket handler for streaming stock prices"""
    client_ip = websocket.remote_address[0]
    logger.info(f"New connection from {client_ip}")
    
    try:
        while True:
            # Generate simulated market data
            market_data = {
                ticker: round(random.uniform(100, 300), 2)
                for ticker in TICKERS
            }
            
            # Add metadata for Application Insights
            properties = {
                'custom_dimensions': {
                    'client_ip': client_ip,
                    'data_points': len(market_data),
                    'tickers': ','.join(TICKERS)
                }
            }
            
            try:
                await websocket.send(json.dumps(market_data))
                logger.info('Stock data sent', extra=properties)
                
                # Send custom telemetry
                if random.random() < 0.1:  # Sample 10% of data points
                    logger.info(
                        'StockPriceSample',
                        extra={'custom_dimensions': market_data}
                    )
                
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"Client {client_ip} disconnected normally")
                break
            except Exception as send_error:
                logger.error(f"Data send error: {str(send_error)}", extra=properties)
                break
            
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra=properties)
    finally:
        await websocket.close()

# ======================
# Server Initialization
# ======================

async def start_servers():
    """Initialize combined HTTP/WebSocket servers"""
    # Create HTTP server for health checks
    http_server = web.Application()
    http_server.add_routes([web.get('/health', health_check)])
    
    # Create WebSocket server
    ws_server = await websockets.serve(
        stock_price_stream,
        '0.0.0.0',
        SERVER_PORT,
        ping_interval=PING_INTERVAL,
        max_size=2**20  # 1MB max message size
    )
    
    # Run both servers
    await asyncio.gather(
        web._run_app(http_server, port=SERVER_PORT, handle_signals=True),
        ws_server.wait_closed()
    )

# ======================
# Entry Point
# ======================

if __name__ == "__main__":
    logger.info(f"Starting server on port {SERVER_PORT}")
    
    try:
        asyncio.run(start_servers())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as critical_error:
        logger.critical(f"Fatal server error: {str(critical_error)}")
        raise
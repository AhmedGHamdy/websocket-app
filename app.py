import asyncio
import websockets
import json
import random
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

# ======================
# Configuration Setup
# ======================

# Azure Application Insights Configuration
connection_string = os.getenv('APPINSIGHTS_CONNECTION_STRING')
if not connection_string:
    raise ValueError("Application Insights connection string not configured")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string=connection_string))

# Application Constants
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]
SERVER_PORT = 8080
PING_INTERVAL = 10  # Seconds between keep-alive pings

# ======================
# WebSocket Server Logic
# ======================

async def maintain_connection(websocket):
    """Maintain WebSocket connection with regular pings"""
    while True:
        try:
            await asyncio.sleep(PING_INTERVAL)
            await websocket.ping()
            logger.debug("Sent keep-alive ping")
        except Exception as e:
            logger.error(f"Connection maintenance failed: {e}")
            break

async def handle_client(websocket, path):
    """Main WebSocket handler for client connections"""
    logger.info(f"New connection from {websocket.remote_address}")
    
    # Start keep-alive task
    keep_alive = asyncio.create_task(maintain_connection(websocket))
    
    try:
        while True:
            # Generate simulated market data
            market_data = {
                ticker: round(random.uniform(100, 300), 2)
                for ticker in TICKERS
            }
            
            # Send data to client
            try:
                await websocket.send(json.dumps(market_data))
                logger.info(f"Sent data: {market_data}")
            except Exception as send_error:
                logger.error(f"Data send failed: {send_error}")
                break
            
            await asyncio.sleep(1)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        keep_alive.cancel()
        await websocket.close()

# ======================
# Server Lifecycle Management
# ======================

async def run_server():
    """Start WebSocket server with proper lifecycle management"""
    server = await websockets.serve(
        handle_client,
        "0.0.0.0",
        SERVER_PORT,
        ping_interval=None,  # We handle pings manually
        max_size=2**20  # 1MB max message size
    )
    
    logger.info(f"WebSocket server started on port {SERVER_PORT}")
    logger.info(f"Server PID: {os.getpid()}")
    
    try:
        await server.wait_closed()
    except asyncio.CancelledError:
        logger.info("Server shutdown initiated")
        server.close()
        await server.wait_closed()

# ======================
# Entry Point
# ======================

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as critical_error:
        logger.critical(f"Fatal server error: {critical_error}")
        raise
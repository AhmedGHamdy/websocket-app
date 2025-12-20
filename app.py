import asyncio
import websockets
import json
import random
from azure.identity import DefaultAzureCredential
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.core.exceptions import AzureError
import os
from azure.monitor.query import MetricsQueryClient

# List of simulated stock tickers
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]

# Environment variables for Azure
sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
resource_group_name = os.getenv("AZURE_RESOURCE_GROUP_NAME")
app_insights_name = os.getenv("AZURE_APP_INSIGHTS_NAME")

# Setup Azure Application Insights client
def get_azure_client():
    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    # Create the Application Insights Management Client
    client = ApplicationInsightsManagementClient(credential=credential, subscription_id=sub_id)
    return client

# Function to send telemetry data to Application Insights
async def send_telemetry(data):
    """
    Send telemetry data to Azure Application Insights
    """
    try:
        # Authenticate and create the client
        client = get_azure_client()

        # Here, we'll simulate sending telemetry data to Application Insights
        # For example, send stock price as custom event to Application Insights
        for ticker, price in data.items():
            # You can add more details or structure depending on your needs
            event_data = {
                "event_name": "stock_price_event",
                "ticker": ticker,
                "price": price
            }

            # Here, you can actually send telemetry events using client methods
            # The current client does not have a direct event tracking method,
            # So you'd use Application Insights SDK for sending events in practice.
            # The idea here is to track custom events as shown:
            print(f"Sending to Application Insights: {event_data}")
        
    except AzureError as e:
        print(f"Error sending telemetry: {e}")

async def stream_stock_data(websocket, path=None):
    """
    WebSocket handler that streams simulated stock prices and sends telemetry
    """
    while True:
        stock_data = {ticker: round(random.uniform(100, 300), 2) for ticker in TICKERS}
        
        # Send stock data to WebSocket clients
        await websocket.send(json.dumps(stock_data))
        
        # Send telemetry data to Application Insights
        await send_telemetry(stock_data)
        
        await asyncio.sleep(1)

async def main():
    """
    Main coroutine to start both WebSocket servers on ports 8080 and 8081.
    """
    async with websockets.serve(stream_stock_data, "0.0.0.0", 8080), \
               websockets.serve(stream_stock_data, "0.0.0.0", 8081):
        # Keep the servers running indefinitely
        await asyncio.Future()

if __name__ == "__main__":
    # Running the WebSocket server
    asyncio.run(main())

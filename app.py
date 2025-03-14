import asyncio
import websockets
import json
import random
from azure.identity import DefaultAzureCredential
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.monitor.query import MetricsQueryClient
from azure.core.exceptions import AzureError
import os

# List of simulated stock tickers
TICKERS = ["AAPL", "TSLA", "GOOG", "AMZN"]

# Application Insights setup
sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
credential = DefaultAzureCredential()
client = ApplicationInsightsManagementClient(credential=credential, subscription_id=sub_id)

# Define your Application Insights resource name and ID
resource_group_name = ""
app_insights_name = "<your-app-insights-name>"

async def send_telemetry(data):
    """
    Send telemetry data to Azure Application Insights
    """
    try:
        # Send telemetry data as events, traces, or custom metrics
        # Example: Send event
        print(f"Sending data to Application Insights: {data}")
        # You would send telemetry here using the Application Insights API
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
    asyncio.run(main())

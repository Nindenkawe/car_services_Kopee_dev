from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiohttp

# Create a FastAPI instance
kopee = FastAPI()

# Mount the "static" directory to serve static files
kopee.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the "templates" directory to serve HTML templates
templates = Jinja2Templates(directory="templates")


class Customer(BaseModel):
    id: int
    tin_number: str
    plate_number: str
    vehicule_model: str


class Transaction(BaseModel):
    id: int
    transaction_id: str
    Transaction_type: str
    provider_id: int
    amount: float
    transaction_status: bool


class DataHandler:
    def __init__(self, api_endpoint: str, timeout: int = 10):
        self.api_endpoint = api_endpoint
        self.timeout = timeout
        self.data = None

    async def fetch_data_from_api(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_endpoint, timeout=self.timeout) as response:
                    if response.status == 200:
                        self.data = await response.json()
                    else:
                        raise HTTPException(status_code=response.status, detail=f"Failed to fetch data from API: {response.status}")
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Error fetching data from API: {e}")


async def get_data(api_endpoint):
    handler = DataHandler(api_endpoint)
    await handler.fetch_data_from_api()
    return handler.data


@kopee.get("/")
async def render_dashboard(request: Request):
    customers_data = await get_data("http://127.0.0.1:8000/car_services/car")
    transactions_data = await get_data("http://127.0.0.1:8000/car_services/transaction")

    # Handle potential errors during data fetching
    if not customers_data or not transactions_data:
        raise HTTPException(status_code=500, detail="Failed to fetch data from one or both endpoints")

    return templates.TemplateResponse(
        "home.html", {"request": request, "customers": customers_data, "transactions": transactions_data}
    )
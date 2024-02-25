from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import aiohttp

# Create a FastAPI instance
kopee = FastAPI()

# Mount the "static" directory to serve static files
kopee.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the "templates" directory to serve HTML templates
templates = Jinja2Templates(directory="templates")

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
    def handle_request_car_servicing(request):
        if request.method == "POST":
            # Get the form data
            form_data = request.form

            # Get the subscriber ID
            subscriber_id = form_data["subscriber_id"]

            # Get the car ID
            car_id = form_data["car_id"]

            # Get the service type
            service_type = form_data["service_type"]

            # Get the service date
            service_date = form_data["service_date"]

            # Get the service time
            service_time = form_data["service_time"]

            # Create a payment request
            payment_request = PaymentRequest(
                payeeNote="Payment for car servicing",
                externalId=f"{subscriber_id}_{car_id}_{service_type}_{service_date}_{service_time}",
                amount="100",
                currency="USD",
                payer=Payer(
                    partyIdType="MSISDN",
                    partyId="0700000000",
                ),
                payerMessage="Please process this payment as soon as possible.",
            )

            # Make the payment
            make_payment(payment_request)

        return templates.TemplateResponse("car_services.html", {"request": request})


@kopee.get("/request_car_servicing")
async def render_car_servicing_form(request: Request):
    return templates.TemplateResponse("car_services.html", {"request": request})

@kopee.get("/subscriber_profile/{id}")
async def get_subscriber_profile(id: int = Path(..., title="The ID of the subscriber profile")):
    handler = DataHandler(f"http://127.0.0.1:7000/car_services/car/{id}", timeout=5)
    await handler.fetch_data_from_api()

    if handler.data:
        return handler.data
    else:
        raise HTTPException(status_code=404, detail=f"Subscriber profile with ID {id} not found")



class Payer(BaseModel):
    partyIdType: str
    partyId: str

class PaymentRequest(BaseModel):
    payeeNote: str
    externalId: str
    amount: str
    currency: str
    payer: Payer
    payerMessage: str

@kopee.post("/make_payment")
async def make_payment(payment_request: PaymentRequest):
    # Authentication token for the MoMo API
    auth_token = "your_auth_token_here"
    
    # Construct headers
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": "FFtw@Lz@6qWR83W",
        "Authorization": f"Bearer {auth_token}"
    }
    
    # Convert the PaymentRequest object to a dictionary
    data = payment_request.dict()
    
    # Make the request to the MoMo API
    response = requests.post("https://sandbox.momodeveloper.mtn.com/collection/v2_0/requesttowithdraw", 
    headers=headers, json=data, timeout=5)
    
    # Check the response status code
    if response.status_code == 202:
        return {"message": "Payment request accepted"}
    elif response.status_code == 400:
        raise HTTPException(status_code=400, detail="Bad request, invalid data was sent")
    elif response.status_code == 409:
        raise HTTPException(status_code=409, detail="Conflict, duplicated reference id")
    elif response.status_code == 500:
        raise HTTPException(status_code=500, detail="Internal server error")
    else:
        raise HTTPException(status_code=500, detail="Unknown error occurred")

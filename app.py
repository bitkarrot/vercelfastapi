from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles 

import datetime
import uvicorn
import os
from ln_address import LNAddress
from aiohttp.client import ClientSession

import pyqrcode
from io import BytesIO

description = " API for getting QR codes and Bolt11 Invoices from Lightning Addresses"

# Get environment variables
invoice_key = os.getenv('INVOICE_KEY')
admin_key = os.getenv('ADMIN_KEY')
base_url =  os.getenv('BASE_URL') 

config = { 'invoice_key': invoice_key, 
            'admin_key': admin_key, 
            'base_url': base_url }

app = FastAPI(
    title="LNaddy.com",
    description=description,
    version="0.0.1",
    contact={
        "name": "bitkarrot",
        "url": "http://github.com/bitkarrot/lnaddy",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

def configure_static(app):  #new
    app.mount("/static", StaticFiles(directory="static"), name="static")

configure_static(app) 


async def get_bolt(email, amount):
    try: 
        async with ClientSession() as session:
            lnaddy = LNAddress(config, session)
            bolt11 = await lnaddy.get_bolt11(email, amount)
            print(bolt11)
            return bolt11
    except Exception as e: 
        print(e)
        return None


@app.get("/")
def main():
    html_content = """
    <html>
        <head>
            <title>LNaddy.com</title>
              <link rel="icon" type="image/x-icon" href="/static/images/favicon.ico">
        </head>
        <body><div align="center">
            <h1> Lightning Addy</h1>
            <img src="/static/images/bitkarrot.jpeg">
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
    # redirect to front end site


@app.get("/example/{parameter}")
def example(parameter: str):
    return {
        "parameter": parameter,
        "datetime": datetime.datetime.now().time()
    }


@app.get('/tip/{lightning_address}')
async def get_Tip_QR_Code(lightning_address: str):
    try:
        print(lightning_address)
        bolt11 = await get_bolt(lightning_address, None)
        # bolt11 = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
        qr = pyqrcode.create(bolt11)
        tip_file = '/tmp/qr_tip.png'
        qr.png(tip_file, scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])
        return FileResponse(tip_file)
    except Exception as e:
        return { 
            "msg" : "Not a valid tipping Address. Sorry!"
        }



@app.get('/qr/{lightning_address}')
async def get_QR_Code_From_LN_Address(lightning_address: str):
    """
    this endpoint returns a QR PNG image when given a Lightning Address.
    example use: /qr/user@mydomain.com
    """
    try:
        if lightning_address is not None:    
            tip_file = '/tmp/qr_lnaddy.png'
            bolt11 = await get_bolt(lightning_address, None)
            # bolt11 = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
            qr = pyqrcode.create(bolt11) 
            qr.png(tip_file, scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])
            return FileResponse(tip_file)
        else: 
            return {
                "msg" : "Please send a valid Lightning Address"
            }
    except Exception as e: 
        return { 
            "msg" : "Not a valid Lightning Address. Sorry!"
        }




@app.get('/bolt11/{bolt11}')
async def get_qr_via_bolt11(bolt11: str):
    """
    this end point returns a QR PNG when given a bolt11 
    example use: /bolt11/LNURL.......
    """
    # bolt11 = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
    try:
        tip_file = '/tmp/qr_tip.png'
        if bolt11 is not None:
            # TODO >>>>> check if bolt11 is valid
            qr = pyqrcode.create(bolt11)
            qr.png(tip_file, scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])
            return FileResponse(tip_file)
        else: 
            return {
                "msg" : "Please send a bolt 11"
            }
    except Exception as e:
        return { 
            "msg" : "Not a valid Bolt11"
        }


@app.get("/img/{lightning_address}")
async def get_svg_img_from_LN_address(lightning_address): 
    """
    this endpoint returns image  in SVG xml format  as part of json response
    example use: /img/user@domain.com
    """
    try: 
        print(lightning_address)
        #bolt11 = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
        bolt11 = await get_bolt(lightning_address, None)
        qr = pyqrcode.create(bolt11)
        
        stream = BytesIO()
        qr.svg(stream, scale=3)

        return (
                stream.getvalue(),
                200,
                {
                    "Content-Type": "image/svg+xml",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                },
        )
    except Exception as e: 
        print(e)
        return { 
            "msg" : "Not a valid Lightning Address"
        }




# not for deploy on vercel
if __name__ == "__main__":
  uvicorn.run("app:app", host="localhost", port=3000, reload=True)
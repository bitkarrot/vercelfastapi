from fastapi import FastAPI
from fastapi.responses import FileResponse
import datetime
import uvicorn

import pyqrcode
from io import BytesIO

description = " API for getting QR codes and Bolt11 Invoices from Lightning Addresses"

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

@app.get("/")
def main():
    # redirect to front end site
    return {
        "message": "Hello my friend"
    }

@app.get("/example/{parameter}")
def example(parameter: str):
    return {
        "parameter": parameter,
        "datetime": datetime.datetime.now().time()
    }

@app.get('/tip')
def get_qrcode():
    sept21pay = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
    qr = pyqrcode.create(sept21pay)
    tip_file = '/tmp/qr_21.png'
    qr.png(tip_file, scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])
    return FileResponse(tip_file)


@app.get('/qr/{addy}')
def get_QR_Code_From_LN_Address(addy: str):
    """
    this endpoint returns a QR PNG image when given a Lightning Address.
    example use: /qr/user@mydomain.com
    """
    try:
        if addy is not None:    
            tip_file = '/tmp/qr_lnaddy.png'
            # TODO: add method to get bolt11 from addy
            bolt11 = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
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
def get_qr_via_bolt11(bolt11: str):
    """
    this end point returns a QR PNG when given a bolt11 
    example use: /bolt11/LNURL.......
    """
    bolt11 = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
    try:
        tip_file = 'images/qr_tip.png'
        if bolt11 is not None:    

            # check if bolt11 is valid
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
def get_svg_img_from_LN_address(lightning_address): 
    """
    this endpoint returns image  in SVG xml format  as part of json response
    example use: /img/user@domain.com
    """
    # TODO: add method to get Bolt11 from addy
    print(lightning_address)
    bolt11 = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
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

# not for deploy on vercel
if __name__ == "__main__":
  uvicorn.run("app:app", host="localhost", port=3000, reload=True)
from fastapi import FastAPI
from fastapi.responses import FileResponse
import datetime
import uvicorn

import pyqrcode
from io import BytesIO

app = FastAPI()

@app.get("/example/{parameter}")
def example(parameter: str):
    return {
        "parameter": parameter,
        "datetime": datetime.datetime.now().time()
    }

@app.get("/")
def main():
    return {
        "message": "Hello my friend"
    }


@app.get('/tip')
def get_qrcode():
    sept21pay = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
    qr = pyqrcode.create(sept21pay)
    tip_file = 'images/qr_21.png'
    qr.png(tip_file, scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])
    return FileResponse(tip_file)


@app.post("/send_image")
async def send():
    sept21pay = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
    qr = pyqrcode.create(sept21pay)
    tip_file = 'images/qr_21.png'
    qr.png(tip_file, scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])

    image = BytesIO()   
    qr.svg(image, scale=3)          # Do something here to create an image
    # image.save(image, format='JPEG', quality=85)   # Save image to BytesIO
    image.seek(0)                                # Return cursor to starting point
    return StreamingResponse(image.read(), media_type="image/jpeg")




@app.get("/img")
def get_img(): 
    withdraw = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7AMFW35XGUNPWUHKZURF9AMRZTMVDE6HYMP02E485MMDG9FHWWZ529H5X46CDF3XWDMFGEDZ742WW33X7AT6VECKUWP5D92Y56RFXEJHJURR7WD75N"
    paylink = "LNURL1DP68GURN8GHJ7CNFW3EJUCNFW33K76TW9EHHYEEWDP4J7MRWW4EXCUP0V9CXJTMKXYHKCMN4WFKZ7VF42FKAHK"
    qr = pyqrcode.create(withdraw)
    qr.png('images/qr_withdraw.png', scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])

    qr = pyqrcode.create(paylink)
    qr.png('images/qr_paylink.png', scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])


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
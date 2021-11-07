import json
import logging
#import os
#import asyncio

from aiohttp.client import ClientSession
from utils import get_url, post_url, post_jurl

###################################
logging.basicConfig(filename='lnaddress.log', level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("lnaddress").setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)
###################################


'''
Async methods for Payment to a LN Address w/LNBits API
'''

class LNAddress:
    def __init__(self, config, session: ClientSession = None):
        self._session = session
        self._inv_key = config['invoice_key']
        self._admin_key = config['admin_key']
        self.base_url = config['base_url']

    # invoice key
    def invoice_headers(self):
        data = {"X-Api-Key": self._inv_key, "Content-type": "application/json"}
        return data

    # admin key
    def admin_headers(self):
        data = {"X-Api-Key": self._admin_key, "Content-type": "application/json"}
        return data

    # standard headers
    def headers(self):
        data = {"Content-type": "text/html; charset=UTF-8"}
        return data

    # works
    def get_payurl(self, email: str) -> str: 
        '''
        Construct Lnurlp link from email address provided. 
        '''
        try:
            parts = email.split('@')
            domain = parts[1]
            username = parts[0]
            transform_url = "http://" + domain + "/.well-known/lnurlp/" + username
            logging.info("Transformed URL:")
            logging.info(transform_url)
            return transform_url
        except Exception as e: 
            logging.error("Exception, possibly malformed LN Address: " + e)
            return {'status' : 'error', 'msg' : 'Possibly a malformed LN Address'}


    # works
    async def get_bolt11(self, email: str, amount: int): 
        '''
            fail state
            {'reason': 'Amount 100 is smaller than minimum 100000.', 'status': 'ERROR'}

            success state
            {'pr': 'lnbc1......azgfe0', 
            'routes': [], 'successAction': {'description': 'Thanks love for the lightning!', 
            'tag': 'url', 'url': 'https:/.......'}}
        '''
        try: 
            purl = self.get_payurl(email)
            # print(purl)
            json_content = await get_url(session=self._session, path=purl, headers=self.headers())
            # print(json_content)
            datablock = json.loads(json_content)
            logging.info(str(datablock))

            lnurlpay = datablock["callback"]
            min_amount = datablock["minSendable"]

            payquery = lnurlpay + "?amount=" + str(min_amount)
            if amount is not None:
                if int(amount*1000) > int(min_amount):
                    payquery = lnurlpay + "?amount=" + str(amount*1000)
            
            logging.info("amount: " + str(amount))
            logging.info("payquery: " + str(payquery))
        
            # TODO: check if URL is legit, else return error
            # get bech32-serialized lightning invoice
            ln_res =  await get_url(session=self._session, path=payquery, headers=self.headers())
            pr_dict = json.loads(ln_res)

            # print('pr', pr_dict)
            # check keys returned for status
            if 'status' in pr_dict: 
                reason = pr_dict['reason']
                return reason
            elif 'pr' in pr_dict: 
                bolt11 = pr_dict['pr']
                return bolt11
            
        except Exception as e: 
            logging.error("in get bolt11 : "  + str(e))
            return {'status': 'error', 'msg': 'Cannot make a Bolt11, are you sure the address is valid?'}



    # get payment hash from bolt11 - use json on post request - works
    async def get_payhash(self, bolt11):
        try:
            decode_url = self.base_url + "/decode"
            payload = {'data': bolt11}
            decoded =  await post_jurl(session=self._session, path=decode_url, json=payload, headers=self.invoice_headers())
            # logging.info(decoded)
            if 'payment_hash' in decoded:
                payhash = decoded['payment_hash']
                logging.info('payment hash: ' + payhash)
                return payhash
        except Exception as e:
            logging.error('Exception in get_payhash() ', str(e))
            return e


    # check payment hash from decoded BOLT11 - works
    async def check_invoice(self, payhash):
        try:
            payhashurl = self.base_url + "/" + str(payhash)
            res =  await get_url(session=self._session, path=payhashurl, headers=self.invoice_headers())
            output = json.loads(res)
            # logging.info("check invoice response: " + output)
            pay_status = output['paid']
            pay_preimage = output['preimage']
            return pay_status, pay_preimage
        except Exception as e:
            logging.error('Exception in get_paystatus() ', str(e))
            return e


    # pay bolt11  - ok works, but use the offical one from pylnbits as it is async
    async def pay_invoice(self, bolt11): 
        '''
        error message:
        {'message': '{"error":"self-payments not allowed","code":2,"message":"self-payments not allowed","details":[]}'}
        '''
        try:
            data = {"out": True, "bolt11": bolt11}
            body = json.dumps(data)
            logging.info(f"body: {body}")
            res =  await post_url(session=self._session, path=self.base_url, body=body, headers=self.admin_headers())
            logging.info(res)
            return res
        except Exception as e: 
            logging.error('Exception in pay_invoices(): ', e)
            return e


'''
async def main():
    email = 'bitkarrot@bitcoin.org.hk'
    # email = 'foo@example.com'
    amount = None 
    amount = 150 # 100 sats
    
    # Get environment variables
    invoice_key = os.getenv('INVOICE_KEY')
    admin_key = os.getenv('ADMIN_KEY')
    base_url =  os.getenv('BASE_URL') 

    config = { 'invoice_key': invoice_key, 
                'admin_key': admin_key, 
                'base_url': base_url }

    async with ClientSession() as session:
        print("in main")
        lnaddy = LNAddress(config, session)
        # ok - works
        bolt11 = await lnaddy.get_bolt11(email, amount)
        print(bolt11)
        #bolt11 = "lnbc1u1pscqezzpp5y620vkqn3h2fuey4qh035w4wescgv84w5wjpm7pz2mkwep208hesdqjw3jhxarfdemx76trv5xqyjw5qcqpjsp55alg0d9xumf00xeh3czdk7cw6rp5258k66ny5flwzm53pyugm5ysrzjq0dtsllcvdvc9q2ug4n7kk90fruegng3c447ky4ercgyn2h2qmscwzj0g5qqthgqqyqqqqqpqqqqqlgq9q9qy9qsq2205evs9kmhs2qpu3vnfp9y628luxsaqh9j8kxvy76ydh0rd7n749wx02dxjs7xs4hm5ythdrj07wxyk7fkv4x2wjc97hnm7smutz7qqm50er9"

        payhash = await lnaddy.get_payhash(bolt11)
        print(payhash)

        status, image = await lnaddy.check_invoice(payhash)
        print('paid status:', status, " image : ", image)

        # pay invoice - ok works
        result = await lnaddy.pay_invoice(bolt11)
        if result is dict:
            print('pay invoice status: ', result)
            payment_hash = result['payment_hash']

        # pay invoice status:  {'checking_id': '2694f658138dd49e649505df1a3aaecc30861eaea3a41df82256ecec854f3df3', 'payment_hash': '2694f658138dd49e649505df1a3aaecc30861eaea3a41df82256ecec854f3df3'}

        # check payment hash status - ok works, got payment hash from paid invoice status
        payment_hash = '2694f658138dd49e649505df1a3aaecc30861eaea3a41df82256ecec854f3df3'
        status, image = await lnaddy.check_invoice(payment_hash)
        print('paid status:', status, " image : ", image)
        



loop = asyncio.get_event_loop()
loop.run_until_complete(main())

'''

import jwt
from jwt import *
import base64

payload = {'park':'madison square'}
algo = 'HS256' #HMAC-SHA 256
secret = 'learning'

encoded_jwt = jwt.encode(payload, secret, algorithm=algo)
print(encoded_jwt)

decoded_jwt = jwt.decode(encoded_jwt, secret, verify=True)
print(decoded_jwt)

decoded_base64 = base64.b64decode(str(encoded_jwt).split(".")[1]+"==")
print(decoded_base64)
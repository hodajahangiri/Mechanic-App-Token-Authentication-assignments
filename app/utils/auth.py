from datetime import datetime, timedelta, timezone
from jose import jwt



SECRET_KEY = 'SUPER Secret Code'

def encode_token(id):
    payload = {
        'iat' : datetime.now(timezone.utc), #issued date
        'exp' : datetime.now(timezone.utc) + timedelta(days=0, hours=1), #expiration data
        'sub' : str(id)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
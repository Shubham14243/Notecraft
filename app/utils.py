import re
import shortuuid
from app.config import Config
import datetime
import jwt
import requests
import logging

logger = logging.getLogger(__name__)


class Validator:
    
    @staticmethod
    def validate_email(email):
        
        pattern = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        expr = re.compile(pattern)

        if expr.fullmatch(email):
            return None
        else:
            return 'Invalid Email!'
        
    @staticmethod
    def validate_name(name):
        
        if len(name) >= 3:
            return None
        return 'Invalid Name!'
    
    @staticmethod
    def validate_password(password):
        
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#!%*?&])[A-Za-z\d@$!%*?&]{5,20}$'
        expr = re.compile(pattern)
        
        if expr.fullmatch(password):
            return None
        else:
            return 'Invalid Password! 5-20 Characters, 1 uppercase, 1 lowercase, 1special character(@$#!%*?&), 1 digit!'
        
    @staticmethod
    def validate_username(username):
        
        pattern = r'^[A-Za-z0-9]{8,40}$'
        expr = re.compile(pattern)
        
        if expr.fullmatch(username):
            return None
        else:
            return 'Invalid Username! 8-40 Characters, Letters and Numbers only!'
        
class Generator:
    
    @staticmethod
    def generate_public_key():
        public_key = shortuuid.ShortUUID().random(length=10)
        return public_key
    
    
class Token:
    
    @staticmethod
    def generate_reset_token(user):
        payload = {
            "user_id": user.id,
            "type": "reset",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }

        return jwt.encode(payload, Config.TOKEN_SECRET, algorithm="HS256")
    
    
    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(token, Config.TOKEN_SECRET, algorithms=["HS256"])

            if data.get("type") != "reset":
                return None

            return data["user_id"]

        except:
            return None

class SendMail:

    BASE_URL = Config.EMAIL_HOST + "/api/mail/send"
    
    @staticmethod
    def send_email(data):
        try:

            if data.get('recipient') == None or data.get('username') == None or data.get('reset_url') == None:
                return False
            
            logger.info(f'Reset-username-{data.get('username')}')
            
            body = {
                "template_id": "3",
                "recipient": [data.get('recipient')],
                "params": {
                    "username": data.get('username'),
                    "reset_url": data.get('reset_url')
                },
                "mailkey": Config.EMAIL_KEY
            }

            # 📡 API call
            response = requests.post(
                SendMail.BASE_URL,
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "*/*"
                },
                timeout=20
            )

            if response.status_code in [200, 201]:
                return True

            return False

        except Exception as e:
            return False
            
    
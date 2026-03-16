import re
import shortuuid

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
        
        pattern = r'^[A-Za-z0-9]{8,25}$'
        expr = re.compile(pattern)
        
        if expr.fullmatch(username):
            return None
        else:
            return 'Invalid Username! 8-25 Characters, Letters and Numbers only!'
        
class Generator:
    
    @staticmethod
    def generate_public_key():
        public_key = shortuuid.ShortUUID().random(length=10)
        return public_key
import pyotp

def verify_otp(secret, otp):
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)


test_secret = pyotp.random_base32()
totp_obj    = pyotp.TOTP(test_secret)

current_code  = totp_obj.now()
wrong_code    = "128372"

print(verify_otp(test_secret, current_code))
print(verify_otp(test_secret, wrong_code))

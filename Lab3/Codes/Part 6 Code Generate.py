import pyotp

secret = pyotp.random_base32()

totp = pyotp.TOTP(secret)

current_otp = totp.now()

print("Current OTP:", current_otp)

entered_otp = current_otp

if totp.verify(entered_otp):
    print("OTP accepted")
else:
    print("OTP rejected")

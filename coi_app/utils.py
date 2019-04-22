import math, random 
from django.template.loader import render_to_string
from django.core.mail import get_connection, send_mail
from django.conf import settings

def send_password_reset_email(name, email, otp, link):
    newName = "Anonymous"
    if(name != None):
        newName = name.capitalize()

    print("name = " + newName)
    print("link = " + link)

    context = {"name" : newName, "otp": otp, "logo_link" : link}

    msg_plain = render_to_string('reset_email.txt', context=context)
    msg_html = render_to_string('reset_email.html', context=context)

    connection = get_connection(host=settings.EMAIL_HOST,
                            port=settings.EMAIL_PORT,
                            username=settings.EMAIL_HOST_USER,
                            password=settings.EMAIL_HOST_PASSWORD,
                            use_tls=settings.EMAIL_USE_TLS)

    send_mail(
        'COI Password reset request confirmation',
        msg_plain,
        settings.EMAIL_HOST_USER,
        [email],
        html_message=msg_html,
        connection=connection,
        fail_silently=False
    )

# function to generate OTP 
def generateOTP() : 
    digits = "0123456789"
    OTP = "" 
    for i in range(4) : 
        OTP += digits[math.floor(random.random() * 10)] 
    return OTP 
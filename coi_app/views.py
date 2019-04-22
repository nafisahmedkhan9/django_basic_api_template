from django.shortcuts import render
from .serializers import *
from .models import *
from .filters import *
from rest_framework import viewsets, status
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from .decorators import is_user_authenticated
import json
from .utils import generateOTP, send_password_reset_email


# Create your views here.

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': f'method {request.method} is not allowed'})
    user_data = json.loads(request.body)
    if User.objects.filter(email=user_data['email']).exists():
        user = User.objects.get(email=user_data['email'])
        userData = user.to_dict()
        userData["picture"] = request.build_absolute_uri(user.picture.url)

        if user.check_password(user_data['password']):
            return JsonResponse({"success": True, "status": "Login Successfull.", "data":{"user": userData, 'access_token':user.token}})
        else:
            return JsonResponse({"success" : False, "status":"Email/password did not match."})    
    else:
        return JsonResponse({"success" : False, "status" : f"Couldn't find your COI Account"})
    
@csrf_exempt
@transaction.atomic
def signup(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'status': f'method {request.method} is not allowed'})
    user_data = json.loads(request.body)
    if User.objects.filter(email=user_data['email']).exists():
        return JsonResponse({"success" : False, "status":"Email alreay exists."})
    else:
        user = User.objects.create_user(user_data["email"], user_data["password"])
        user.name = user_data["name"]
        user.email = user_data["email"]
        user.save()
        userData = user.to_dict()
        userData["picture"] = request.build_absolute_uri(user.picture.url)
        return JsonResponse({"success": True, "status": "Successfully registered.", "data":{"user": userData, "access_token": user.token}})

@csrf_exempt
@transaction.atomic
def socialLogin(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "status": f"method {request.method} is not allowed."})
    
    user_data = request.POST.dict()
    try:
        profile_image = request.FILES['picture']
        print("get picture")
    except KeyError:
        print("not get picture")
        print(KeyError)
        profile_image = ""

    if User.objects.filter(email=user_data["email"]).exists():
        user = User.objects.get(email=user_data["email"])
        if user_data["type"] == "google":
            user.google_id = user_data["id"]
        else:
            user.facebook_id = user_data["id"]
        user.name = user_data["name"] if user_data["name"] else user.name
        user.dob = user_data["dob"] if user_data["dob"] else user.dob
        user.gender = user_data["gender"] if user_data["gender"] else user.gender
        user.picture = profile_image if profile_image else "image/default_image.png"
        user.save()
        userData = user.to_dict()
        userData["picture"] = request.build_absolute_uri(user.picture.url)
        return JsonResponse({"success": True, "status": "Login Successfull.", "data":{"user": userData, 'access_token':user.token}})
    else:
        try:
            with transaction.atomic():
                if user_data["type"] == "google":
                    user = User(email=user_data["email"], google_id=user_data["id"])
                else:
                    user = User(email=user_data["email"], facebook_id=user_data["id"])
                user.name = user_data["name"] if user_data["name"] else user.name
                user.dob = user_data["dob"] if user_data["dob"] else user.dob
                user.gender = user_data["gender"] if user_data["gender"] else user.gender
                user.picture = profile_image if profile_image else "image/default_image.png"
                user.save()
                userData = user.to_dict()
                userData["picture"] = request.build_absolute_uri(user.picture.url)

                return JsonResponse({"success": True, "status": "Login Successfull.", "data":{"user": userData, "access_token": user.token}})
        except Exception as e:
            return JsonResponse({"success": False, "status": str(e)})

@csrf_exempt
def is_fbuser_present(request):
    if request.method != 'GET':
        return JsonResponse({"success" : False, "status" : f"Method {request.method} not allowed"})
    fb_id = request.GET['id']
    if User.objects.filter(facebook_id=fb_id).exists():
        users = User.objects.filter(facebook_id=fb_id)
        for user in users:
            if user.email and user.email != "":
                userData = user.to_dict()
                return JsonResponse({"success" : True, "status" : "Facebook id is present", "data":{"user": userData, "access_token": user.token}})
        return JsonResponse({"success" : False, "status" : "Facebook id with email not found"})
    else:
        return JsonResponse({"success" : False, "status" : "Facebook id not found"})

@csrf_exempt
def sendOtp(request):
    if request.method != 'POST':
        return JsonResponse({"success" : False, "status" : f"Method {request.method} not allowed"})

    user_data = json.loads(request.body)
    email = user_data["email"]
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email) 
        otp = generateOTP()
        user.otp = otp
        user.save()
        print("name", user.name)
        send_password_reset_email(user.name, email, otp, "image/coi.jpg")
        return JsonResponse({"success" : True, "status": f"OTP is sent to {email}", "otp": otp})
    else:
        return JsonResponse({"success" : False, "status" : f"Couldn't find your COI Account"})

@csrf_exempt
@is_user_authenticated
def change_password(request):
    if request.method != "POST":
        return JsonResponse({"success" : False, "status" : f"Method {request.method} not allowed"})
    try:    
        user = request.user 
        user_data = json.loads(request.body)
        if user_data["type"] == "social":
            new_password = user_data["new_password"]
            user.set_password(new_password)
            user.save()
            return JsonResponse({"success": True, "status": "Password is changed. Now you can signin with your new password"})
        elif user_data["type"] == "normal":
            old_password = user_data["old_password"]
            new_password = user_data["new_password"]
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return JsonResponse({"success": True, "status": "Password is changed. Now you can signin with your new password."})
            else: 
                return JsonResponse({"success": False, "status": "Wrong Password.Try again"})
        else:
            return JsonResponse({"success": False, "status": "type is not correct."})
        
    except Exception as e:
        return JsonResponse({"success": False, "status": str(e)})
        
@csrf_exempt
def verify_otp(request):
    if request.method != 'POST':
        return JsonResponse({"success" : False, "status" : f"Method {request.method} not allowed"})

    user_data = json.loads(request.body)
    email = user_data["email"]
    otp = user_data['otp']
    try:
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.otp == otp:
                user.otp = ""
                user.is_otp_verified = True
                user.save()
                return JsonResponse({"success" : True, "status" : "Your password reset otp is verified."})
            else:
                return JsonResponse({"success" : False, "status" : "Your password reset OTP not valid or expired."})		
        else:
            return JsonResponse({"success" : False, "status" : f"Couldn't find your COI Account"})
    except Exception as e:
        return JsonResponse({"success" : False, "status" : str(e)})

@csrf_exempt
def resetPassword(request):
    if request.method != 'GET':
        return JsonResponse({"success" : False, "status" : f"Method {request.method} not allowed"})

    user_data = json.loads(request.body)
    email = user_data['email']
    newpassword = user_data['newpassword']
    try:	
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_otp_verified:
                user.is_otp_verified = False
                user.set_password(newpassword)
                user.save()
                return JsonResponse({"success" : True, "status" : "Your password has been changed. You can now signin with your new credentials."})
            else:
                return JsonResponse({"success" : False, "status" : "Your otp is not verified."})
        else:
            return JsonResponse({"success" : False, "status" : f"Couldn't find your COI Account"})
    except Exception as e:
        return JsonResponse({"success" : False, "status" : str(e)})

@csrf_exempt
@is_user_authenticated
def update_mobile_number(request):
    if request.method != "GET":
        return JsonResponse({"success" : False, "status" : f"Method {request.method} not allowed"})
    try:
        mobile = request.GET['mobile']
        user = request.user
        otp = generateOTP()
        user.otp = otp
        user.save()
        sendOtpResp = sendMessage(f"Your Brand Factory OTP code is : {otp}", mobile)
        if(sendOtpResp[:4] == "1701"):
            return JsonResponse({"success":True, "status":"otp is sent", "otp": otp})
        else:
            return JsonResponse({"success":False, "status":"Otp is not sent. Please check your mobile number"})
    except Exception as e:
        return JsonResponse({"success": False, "status": str(e)})

@csrf_exempt
@is_user_authenticated
def verify_mobile_otp(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "status": f"Methos {request.method} is not allowed"})
    try:
        mobile = request.GET['mobile']
        otp = request.GET["otp"]
        user = request.user
        user_otp = user.otp
        if otp == user_otp:
            user.mobile = mobile
            user.save()
            userData = user.to_dict()
            userData["picture"] = request.build_absolute_uri(user.picture.url)
            return JsonResponse({"success": True, "status": "Otp is verified", "data":{"user": userData, 'access_token':user.token}})
        else:
            return JsonResponse({"success":False, "status":"Otp is not correct. Please try again."})
    except Exception as e:
        return JsonResponse({"success": False, "status": str(e)})

class UserViewSet(viewsets.ModelViewSet):
    filter_class = UserFilter
    serializer_class = UserSerialzer
    queryset = User.objects.all()

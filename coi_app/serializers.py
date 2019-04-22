from rest_framework import serializers
from .models import * 

class UserSerialzer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "name", "id", "picture", "facebook_id", "google_id", "dob", "mobile", "gender")
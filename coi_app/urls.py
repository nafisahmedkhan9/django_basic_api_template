    
from django.urls import path, include
from rest_framework import routers
from .views import *
from . import views
from django.conf import settings
from django.conf.urls.static import static

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register('user', UserViewSet)
# router.register('customer', CustomerViewSet)
# router.register('transaction', TransactionViewSet)
# router.register('product', ProductViewSet)
# router.register('expense', ExpenseViewSet)
# router.register('payment', PaymentViewSet)
# router.register('stock', StockViewSet)

app_name  = "coi_app"
urlpatterns = [
    path('', include(router.urls)),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path('send_otp/', views.sendOtp, name="send otp to mobile and email"),
    path("verify_otp/", views.verify_otp, name="verify one time password"),
    path('reset_password/', views.resetPassword, name="resetting password"),
    path("social_login/", views.socialLogin, name="login with social network"),
    path('is_fbuser_present/', views.is_fbuser_present, name="check is_facebook user present"),
]
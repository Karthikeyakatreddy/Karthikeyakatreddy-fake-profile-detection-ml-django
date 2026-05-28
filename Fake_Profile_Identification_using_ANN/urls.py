from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import views as mainView
from admins import views as admins
from users import views as usr

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", mainView.index, name="index"),
    path("index/", mainView.index, name="index"),
    path("AdminLogin/", mainView.AdminLogin, name="AdminLogin"),
    path("UserLogin/", mainView.UserLogin, name="UserLogin"),
    path("UserRegister/", mainView.UserRegister, name="UserRegister"),

    path("AdminHome/", admins.AdminHome, name="AdminHome"),
    path("AdminLoginCheck/", admins.AdminLoginCheck, name="AdminLoginCheck"),
    path("RegisterUsersView/", admins.RegisterUsersView, name="RegisterUsersView"),
    path("ActivateUsers/", admins.activate_user, name="ActivateUsers"),

    path("UserRegisterActions/", usr.UserRegisterActions, name="UserRegisterActions"),
    path("UserLoginCheck/", usr.UserLoginCheck, name="UserLoginCheck"),
    path("UserHome/", usr.UserHome, name="UserHome"),
    path("DatasetView/", usr.DatasetView, name="DatasetView"),
    path("training/", usr.training, name="training"),
    path("predictTrustWorthy/", usr.predictTrustWorthy, name="predictTrustWorthy"),
    path("prediction/", usr.predictTrustWorthy, name="prediction"),
    path("report/", usr.report_view, name="report"),
    path("result/", usr.report, name="result"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

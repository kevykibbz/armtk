
from django.urls import path
from django import views
from . import views
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('',Dashboard.as_view(),name='manager dashboard'),
    path('dashboard/',views.home,name='home'),
    path('new/user/',newUser.as_view(),name='new user'),
    path('<username>/',ProfileView.as_view(),name='user profile'),
    path('view/users/',views.viewUsers,name='view users'),
    path('password/change/',views.passwordChange,name='user password change form'),
    path('view/orders/',views.viewOrders,name='view orders'),
    path('order/summary/',views.orderSummary,name='order summary'),
    path('edit/main/order/<int:id>/',views.editMainOrder,name='edit main order'), 
    path('edit/order/<int:id>/',EditOrder.as_view(),name='edit order'), 
    path('delete/order/item/<int:id>/',views.deleteSingleItem,name='delete single order item'),
    path('file/upload/<int:id>/',views.handleUpload,name='file upload'),
    path('delete/order/<int:id>/',views.deleteOrder,name='delete order'),
    path('tabulate/order/<int:id>/',TabulateOrder.as_view(),name='tabulate order'),
    path('user/file/uploads/',views.UserUploads,name='user file uploads'),
    path('user/file/uploads/delete/<int:id>/',views.UserUploadsDelete,name='user file uploads delete'),
    path('new/order/',UserNewOrder.as_view(),name='userorder'),
    path('edit/user/<int:id>/',EditUser.as_view(),name='edit user'),
    path('delete/user/<int:id>/',views.deleteUser,name='delete user'),
    path('accounts/logout/',views.user_logout,name='logout'),
    path('accounts/reset_password/',auth_views.PasswordResetView.as_view(form_class=UserResetPassword,template_name='manager/password_reset.html'),name='reset_password'),
    path('accounts/reset_password_done/',auth_views.PasswordResetDoneView.as_view(template_name='manager/password_reset_done.html'),name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='manager/password_reset_confirm.html'),name='password_reset_confirm'),
    path('accounts/reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='manager/password_reset_complete.html'),name='password_reset_complete'),
]
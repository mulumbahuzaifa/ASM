from django.urls import path
from . import views

urlpatterns = [
path('',views.index,name='index'),
path('/dashboard',views.dashboard,name='dashboard'),
path('/container_dashboard',views.containerDashboard,name='container_dashboard'),
path('/disp_images',views.renderImages,name='renderImages'),
path('cont_operations',views.containerOperations,name='containerOperations'),
]

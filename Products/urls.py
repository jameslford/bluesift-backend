from django.urls import path, include, re_path
import views

urlpatterns = [
    path('all', views.product_list),
    path('detail/<int:id>', views.ProductDetail.as_view())
]
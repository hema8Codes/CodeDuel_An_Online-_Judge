from django.urls import path
from .views import ProblemsListAPIView, ProblemsDetailAPIView, ExecuteCodeAPIView

urlpatterns = [
    path('problems/', ProblemsListAPIView.as_view(), name='problem-list'),
    path('problem/<int:pk>/', ProblemsDetailAPIView.as_view(), name='problem-detail'),
    path('execute/', ExecuteCodeAPIView.as_view(), name='execute'),
    
]

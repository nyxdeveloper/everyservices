# django
from django.urls import path

# rest framework
from rest_framework.routers import DefaultRouter

# локальные импорты
from .views import PortfolioView
from .views import SendGradeView
from .views import PrivacyView
from .views import TimeView
from .views import PortfolioViewSet

router = DefaultRouter()

router.register("user_landing", PortfolioViewSet)

urlpatterns = [
    path("landing/<str:pk>/", PortfolioView.as_view(), name="landing"),
    path("landing/grade/<str:pk>/", SendGradeView.as_view(), name="grade"),
    path("privacy/", PrivacyView.as_view(), name="privacy"),
    path("get_free_time/<int:service>/<str:date>/", TimeView.as_view(), name="free_time"),
]

urlpatterns += router.urls

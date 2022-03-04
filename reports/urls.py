# rest framework
from rest_framework.routers import DefaultRouter

# локальные импорты
from .views import ReportViewSet

router = DefaultRouter()

router.register("", ReportViewSet)

urlpatterns = router.urls

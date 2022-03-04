# rest framework
from rest_framework.routers import DefaultRouter

# локальные импорты
from .views import RecordViewSet

router = DefaultRouter()

router.register("", RecordViewSet)

urlpatterns = router.urls

# rest framework
from rest_framework.routers import DefaultRouter

# локальные импорты
from .views import ServiceViewSet

router = DefaultRouter()

router.register("services", ServiceViewSet)

urlpatterns = router.urls

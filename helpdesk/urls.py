# rest framework
from rest_framework.routers import DefaultRouter

# локальные импорты
from .views import HelpdeskMessageViewSet

router = DefaultRouter()

router.register("", HelpdeskMessageViewSet)

urlpatterns = router.urls

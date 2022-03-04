# rest framework
from rest_framework.routers import DefaultRouter

# локальные импорты
from .views import ClientContactViewSet

router = DefaultRouter()

router.register("contacts", ClientContactViewSet)

urlpatterns = router.urls

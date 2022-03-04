# rest framework
from rest_framework.routers import DefaultRouter

# локальные импорты
from .views import Authentication
from .views import Profile

router = DefaultRouter()

router.register("authentication", Authentication)
router.register("profile", Profile)

urlpatterns = router.urls

# rest framework
from rest_framework.routers import DefaultRouter

# локальные импорты
from .views import ScheduleViewSet
from .views import SpecialSchedulesViewSet

router = DefaultRouter()

router.register("schedules", ScheduleViewSet)
router.register("special_schedules", SpecialSchedulesViewSet)

urlpatterns = router.urls

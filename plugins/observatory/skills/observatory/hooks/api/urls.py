"""hooks app URL configuration."""
from rest_framework.routers import DefaultRouter
from observatory.api_utils import generate_app_api

router = DefaultRouter()
generate_app_api('hooks', router)

urlpatterns = router.urls

"""output_styles app URL configuration."""
from rest_framework.routers import DefaultRouter
from observatory.api_utils import generate_app_api

router = DefaultRouter()
generate_app_api('output_styles', router)

urlpatterns = router.urls

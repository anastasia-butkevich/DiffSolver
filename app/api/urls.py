from rest_framework import routers
from app.api.views import DifferentialEqViewSet


app_name = 'api_app'

router = routers.DefaultRouter()
router.register(r'differentialeq', DifferentialEqViewSet, basename='create')
urlpatterns = router.urls

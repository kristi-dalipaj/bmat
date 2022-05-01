from django.urls import path, include
from rest_framework import routers

from works.views import WorkViewSet

router = routers.SimpleRouter()
router.register(prefix="", viewset=WorkViewSet, basename="Works")
urlpatterns = [
    path('', include(router.urls))
]

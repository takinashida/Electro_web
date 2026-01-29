from rest_framework.routers import DefaultRouter
from .views import NetworkNodeViewSet, ProductViewSet

router = DefaultRouter()
router.register("network-nodes", NetworkNodeViewSet)
router.register("product", ProductViewSet)

urlpatterns = router.urls

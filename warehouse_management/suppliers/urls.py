from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, SupplierProductViewSet, ProductViewSet


router = DefaultRouter()
router.register("suppliers", SupplierViewSet, basename="supplier")

router.register("supplier-products",SupplierProductViewSet,basename="supplier-product")


router.register("products", ProductViewSet, basename="product")






urlpatterns = router.urls
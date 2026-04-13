from .common_dq import collect_common_dq_metrics
from .customers_dq import collect_customers_dq_metrics
from .order_items_dq import collect_order_items_dq_metrics
from .order_payments_dq import collect_order_payments_dq_metrics
from .order_reviews_dq import collect_order_reviews_dq_metrics
from .orders_dq import collect_orders_dq_metrics
from .products_dq import collect_products_dq_metrics
from .sellers_dq import collect_sellers_dq_metrics
from .geolocation_dq import collect_geolocation_dq_metrics
from .product_category_name_dq import collect_product_category_name_dq_metrics


TABLE_DQ_METRICS = {
    "customers": collect_customers_dq_metrics,
    "order_items": collect_order_items_dq_metrics,
    "order_payments": collect_order_payments_dq_metrics,
    "order_reviews": collect_order_reviews_dq_metrics,
    "orders": collect_orders_dq_metrics,
    "products": collect_products_dq_metrics,
    "sellers": collect_sellers_dq_metrics,
    "geolocation": collect_geolocation_dq_metrics,
    "product_category_name": collect_product_category_name_dq_metrics,
}

__all__ = ["collect_common_dq_metrics", "write_dq_metrics"]

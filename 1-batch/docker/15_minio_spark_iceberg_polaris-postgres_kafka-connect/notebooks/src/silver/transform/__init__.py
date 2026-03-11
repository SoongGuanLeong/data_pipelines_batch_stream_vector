from .customers import transform_customers
from .order_items import transform_order_items
from .order_payments import transform_order_payments
from .order_reviews import transform_order_reviews
from .orders import transform_orders
from .products import transform_products
from .sellers import transform_sellers

TABLE_TRANSFORMS = {
    "customers": transform_customers,
    "order_items": transform_order_items,
    "order_payments": transform_order_payments,
    "order_reviews": transform_order_reviews,
    "orders": transform_orders,
    "products": transform_products,
    "sellers": transform_sellers,
}

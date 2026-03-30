from .customers import transform_customers
from .order_items import transform_order_items
from .order_payments import transform_order_payments
from .order_reviews import transform_order_reviews
from .orders import transform_orders
from .products import transform_products
from .sellers import transform_sellers
from .geolocation import transform_geolocation
from .product_category_name import transform_product_category_name

TABLE_TRANSFORMS = {
    "customers": transform_customers,
    "order_items": transform_order_items,
    "order_payments": transform_order_payments,
    "order_reviews": transform_order_reviews,
    "orders": transform_orders,
    "products": transform_products,
    "sellers": transform_sellers,
    "geolocation": transform_geolocation,
    "product_category_name": transform_product_category_name,
}

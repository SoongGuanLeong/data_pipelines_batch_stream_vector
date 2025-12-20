# Tables

| csv                                   | columns                                                                                                                                                                                    |
|---------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| olist_customers_dataset.csv           | customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state                                                                                             |
| olist_geolocation_dataset.csv         | geolocation_zip_code_prefix,geolocation_lat,geolocation_lng,geolocation_city,geolocation_state                                                                                   |
| olist_order_items_dataset.csv         | order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value                                                                                          |
| olist_order_payments_dataset.csv      | order_id,payment_sequential,payment_type,payment_installments,payment_value                                                                                                      |
| olist_order_reviews_dataset.csv       | review_id,order_id,review_score,review_comment_title,review_comment_message,review_creation_date,review_answer_timestamp                                                     |
| olist_orders_dataset.csv              | order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date      |
| olist_products_dataset.csv            | product_id,product_category_name,product_name_lenght,product_description_lenght,product_photos_qty,product_weight_g,product_length_cm,product_height_cm,product_width_cm |
| olist_sellers_dataset.csv             | seller_id,seller_zip_code_prefix,seller_city,seller_state                                                                                                                          |
| product_category_name_translation.csv | product_category_name,product_category_name_english                                                                                                                                        |



## ERD - entity relationship diagram

- Mermaid cheat sheet to remember
```
||--o{   = 1 to many
||--||   = 1 to 1
o|--o{   = 0..1 to many
```
- Geolocations table is dirty, duplicated, or derived → no FK

```mermaid
erDiagram
    CUSTOMERS {
        string customer_id PK
        string customer_unique_id
        string customer_zip_code_prefix
        string customer_city
        string customer_state
    }

    ORDERS {
        string order_id PK
        string customer_id FK
        string order_status
        datetime order_purchase_timestamp
        datetime order_approved_at
        datetime order_delivered_carrier_date
        datetime order_delivered_customer_date
        datetime order_estimated_delivery_date
    }

    ORDER_ITEMS {
        string order_id FK
        int order_item_id
        string product_id FK
        string seller_id FK
        datetime shipping_limit_date
        numeric price
        numeric freight_value
    }

    PRODUCTS {
        string product_id PK
        string product_category_name FK
        int product_name_length
        int product_description_length
        int product_photos_qty
        numeric product_weight_g
        numeric product_length_cm
        numeric product_height_cm
        numeric product_width_cm
    }

    SELLERS {
        string seller_id PK
        string seller_zip_code_prefix FK
        string seller_city
        string seller_state
    }

    ORDER_PAYMENTS {
        string order_id FK
        int payment_sequential
        string payment_type
        int payment_installments
        numeric payment_value
    }

    ORDER_REVIEWS {
        string review_id PK
        string order_id FK
        int review_score
        string review_comment_title
        string review_comment_message
        datetime review_creation_date
        datetime review_answer_timestamp
    }

    GEOLOCATIONS {
        string geolocation_zip_code_prefix
        numeric geolocation_lat
        numeric geolocation_lng
        string geolocation_city
        string geolocation_state
    }

    PRODUCT_CATEGORIES {
        string product_category_name PK
        string product_category_name_english
    }

    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : appears_in
    SELLERS ||--o{ ORDER_ITEMS : fulfills
    ORDERS ||--o{ ORDER_PAYMENTS : has
    ORDERS ||--o{ ORDER_REVIEWS : receives
    PRODUCT_CATEGORIES ||--o{ PRODUCTS : categorizes

```
# The Gold Layer Rules
## Rule 1: Grain First (MOST IMPORTANT)
```
Define the grain BEFORE doing anything:
“One row in this table represents ______”
```
## Rule 2: Safe Join Rule
```
Only join if it does NOT change the row count of your fact table
```
## Rule 3: Metric Integrity Rule
```
Never duplicate additive metrics across rows
```
## Rule 4: One Fact = One Process
```
Each fact table represents ONE business event/process
```
## Rule 5: Controlled Flattening
```
Pre-join ONLY low-cardinality attributes that are frequently used
```
## Rule 6: Keep Join Keys
```
Always keep business keys (order_id, etc.) even after denormalization.
(Unless in very strict warehouses)
```

# Plan out the blueprint
Because I'm kinda new so I made the plan out first.
```mermaid
erDiagram
    DIM_CUSTOMERS {
        integer customer_sk PK
        string customer_id
        string customer_unique_id
        string customer_zip_code_prefix
        string customer_city
        string customer_state
        decimal geolocation_lat
        decimal geolocation_lng
    }

    FACT_ORDERS {
        string order_id PK
        integer customer_sk FK
        string customer_id
        string order_status
        integer order_purchase_date_sk FK
        timestamp order_purchase_timestamp
        timestamp order_approved_at
        timestamp order_delivered_carrier_date
        integer order_delivered_customer_date_sk FK
        timestamp order_delivered_customer_date
        timestamp order_estimated_delivery_date
    }

    FACT_ORDER_ITEMS {
        string order_id PK
        integer order_item_id PK
        integer product_sk FK
        integer seller_sk FK
        integer customer_sk FK
        string product_id
        string seller_id
        string customer_id
        timestamp shipping_limit_date
        decimal price
        decimal freight_value
        string order_status
        integer order_purchase_date_sk FK
        timestamp order_purchase_timestamp
        timestamp order_approved_at
        timestamp order_delivered_carrier_date
        integer order_delivered_customer_date_sk FK
        timestamp order_delivered_customer_date
        timestamp order_estimated_delivery_date
    }

    FACT_ORDER_PAYMENTS {
        string order_id PK
        integer payment_sequential PK
        string payment_type
        integer payment_installments
        decimal payment_value
        integer customer_sk FK
        string customer_id
        integer order_purchase_date_sk FK
        timestamp order_purchase_timestamp
    }

    FACT_ORDER_REVIEWS {
        string review_id PK
        string order_id FK
        integer review_score
        string review_comment_title
        string review_comment_message
        integer review_creation_date_sk FK
        timestamp review_creation_date
        integer review_answer_date_sk FK
        timestamp review_answer_timestamp
        integer customer_sk FK
        string customer_id
    }

    DIM_PRODUCTS {
        integer product_sk PK
        string product_id 
        string product_category_name
        string product_category_name_english
        integer product_name_length
        integer product_description_length
        integer product_photos_qty
        decimal product_weight_g
        decimal product_length_cm
        decimal product_height_cm
        decimal product_width_cm
        decimal product_volume_cm3
    }

    DIM_SELLERS {
        integer seller_sk PK
        string seller_id
        string seller_zip_code_prefix
        string seller_city
        string seller_state
        decimal geolocation_lat
        decimal geolocation_lng
    }

    DIM_DATES {
        integer date_sk PK
        date ds
        integer year
        integer quarter
        integer month
        integer day
        integer weekday
        integer is_weekend
        integer is_holiday
    }

    DIM_CUSTOMERS ||--o{ FACT_ORDERS : ""
    DIM_DATES ||--o{ FACT_ORDERS : ""
    DIM_PRODUCTS ||--o{ FACT_ORDER_ITEMS : ""
    DIM_SELLERS ||--o{ FACT_ORDER_ITEMS : ""
    DIM_CUSTOMERS ||--o{ FACT_ORDER_ITEMS : ""
    DIM_DATES ||--o{ FACT_ORDER_ITEMS : ""
    DIM_CUSTOMERS ||--o{ FACT_ORDER_PAYMENTS : ""
    DIM_DATES ||--o{ FACT_ORDER_PAYMENTS : ""
    DIM_CUSTOMERS ||--o{ FACT_ORDER_REVIEWS : ""
    DIM_DATES ||--o{ FACT_ORDER_REVIEWS : ""

```
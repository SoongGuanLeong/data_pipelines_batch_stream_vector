Here’s a **compact CDC cheat sheet** for your 7 `oltp` tables. This shows **Postgres operations** → **expected Kafka/AKHQ event**. Perfect for testing CDC end-to-end.

---

## 1️⃣ Customers

| Operation | SQL Example                                                                                                                                                         | Kafka `"op"` | `"before"` / `"after"`                 |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | -------------------------------------- |
| Insert    | `sql INSERT INTO oltp.customers (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state) VALUES ('c1','c1','12345','CITY','SP');` | `"c"`        | `"before": null` / `"after": {...}"`   |
| Update    | `sql UPDATE oltp.customers SET customer_city='NEW_CITY' WHERE customer_id='c1';`                                                                                    | `"u"`        | `"before": {...}"` / `"after": {...}"` |
| Delete    | `sql DELETE FROM oltp.customers WHERE customer_id='c1';`                                                                                                            | `"d"`        | `"before": {...}"` / `"after": null`   |

---

## 2️⃣ Orders

| Operation | SQL Example                                                                                   | Kafka `"op"` | `"before"` / `"after"`                 |
| --------- | --------------------------------------------------------------------------------------------- | ------------ | -------------------------------------- |
| Insert    | `INSERT INTO oltp.orders (order_id, customer_id, order_status) VALUES ('o1','c1','created');` | `"c"`        | `"before": null` / `"after": {...}"`   |
| Update    | `UPDATE oltp.orders SET order_status='shipped' WHERE order_id='o1';`                          | `"u"`        | `"before": {...}"` / `"after": {...}"` |
| Delete    | `DELETE FROM oltp.orders WHERE order_id='o1';`                                                | `"d"`        | `"before": {...}"` / `"after": null`   |

---

## 3️⃣ Products

| Operation | SQL Example                                                                           | Kafka `"op"` |
| --------- | ------------------------------------------------------------------------------------- | ------------ |
| Insert    | `INSERT INTO oltp.products (product_id, product_category_name) VALUES ('p1','cat1');` | `"c"`        |
| Update    | `UPDATE oltp.products SET product_category_name='cat2' WHERE product_id='p1';`        | `"u"`        |
| Delete    | `DELETE FROM oltp.products WHERE product_id='p1';`                                    | `"d"`        |

---

## 4️⃣ Sellers

| Operation | SQL Example                                                               | Kafka `"op"` |
| --------- | ------------------------------------------------------------------------- | ------------ |
| Insert    | `INSERT INTO oltp.sellers (seller_id, seller_city) VALUES ('s1','CITY');` | `"c"`        |
| Update    | `UPDATE oltp.sellers SET seller_city='NEW_CITY' WHERE seller_id='s1';`    | `"u"`        |
| Delete    | `DELETE FROM oltp.sellers WHERE seller_id='s1';`                          | `"d"`        |

---

## 5️⃣ Order Items

| Operation | SQL Example                                                                                      | Kafka `"op"` |
| --------- | ------------------------------------------------------------------------------------------------ | ------------ |
| Insert    | `INSERT INTO oltp.order_items (order_id, product_id, price, quantity) VALUES ('o1','p1',100,1);` | `"c"`        |
| Update    | `UPDATE oltp.order_items SET quantity=2 WHERE order_id='o1' AND product_id='p1';`                | `"u"`        |
| Delete    | `DELETE FROM oltp.order_items WHERE order_id='o1' AND product_id='p1';`                          | `"d"`        |

---

## 6️⃣ Order Payments

| Operation | SQL Example                                                                                                | Kafka `"op"` |
| --------- | ---------------------------------------------------------------------------------------------------------- | ------------ |
| Insert    | `INSERT INTO oltp.order_payments (order_id, payment_type, payment_value) VALUES ('o1','credit_card',100);` | `"c"`        |
| Update    | `UPDATE oltp.order_payments SET payment_value=120 WHERE order_id='o1';`                                    | `"u"`        |
| Delete    | `DELETE FROM oltp.order_payments WHERE order_id='o1';`                                                     | `"d"`        |

---

## 7️⃣ Order Reviews

| Operation | SQL Example                                                                                | Kafka `"op"` |
| --------- | ------------------------------------------------------------------------------------------ | ------------ |
| Insert    | `INSERT INTO oltp.order_reviews (review_id, order_id, review_score) VALUES ('r1','o1',5);` | `"c"`        |
| Update    | `UPDATE oltp.order_reviews SET review_score=4 WHERE review_id='r1';`                       | `"u"`        |
| Delete    | `DELETE FROM oltp.order_reviews WHERE review_id='r1';`                                     | `"d"`        |

---

### ✅ How to use this cheat sheet

1. Open **AKHQ** or **console consumer** for each table topic
2. Perform the **insert/update/delete** in Postgres
3. Observe that:

   * `"op"` matches the operation (`c/u/d`)
   * `"before"` / `"after"` match the row data
4. Repeat for all 7 tables
5. This proves **full end-to-end CDC**

---

If you want, I can also **draw a mini diagram showing the full flow** from Postgres → Debezium → Kafka → AKHQ with **before/after fields**. It’s super handy for reference. Do you want me to do that?

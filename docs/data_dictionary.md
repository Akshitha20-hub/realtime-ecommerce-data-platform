# Data Dictionary — Real-Time E-Commerce Platform

This data dictionary documents the schemas, data types, business rules, and constraints for all raw transactional and behavioral datasets generated in Phase 1.

---

## 1. Customers (`data/raw/customers.csv`)
Represents registered user profiles on the e-commerce platform.

| Column Name | Data Type | Primary / Foreign Key | Nullable | Description & Business Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_id` | String | **Primary Key** | No | Unique identifier formatted as `CUST-XXXXXX`. | `CUST-000001` |
| `first_name` | String | None | No | Customer's first name. | `James` |
| `last_name` | String | None | No | Customer's surname/family name. | `Smith` |
| `email` | String | None | No | Synthetic contact email address. | `james.smith1@gmail.com` |
| `gender` | String | None | No | Gender indicator: `M`, `F`, or `Other`. | `M` |
| `age` | Integer | None | No | Age in years (bounded between 18 and 72). | `34` |
| `city` | String | None | No | Primary residence municipality. | `New York` |
| `state` | String | None | No | 2-letter state code. | `NY` |
| `signup_date` | Timestamp | None | No | Account registration timestamp (`YYYY-MM-DD HH:MM:SS`). Strictly precedes any customer orders. | `2024-05-14 09:23:11` |
| `customer_segment`| String | None | No | Marketing classification: `Consumer` (65%), `Corporate` (15%), `Small Business` (15%), or `VIP` (5%). | `Consumer` |

---

## 2. Products (`data/raw/products.csv`)
The catalog of goods offered across retail categories.

| Column Name | Data Type | Primary / Foreign Key | Nullable | Description & Business Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | String | **Primary Key** | No | Unique product identifier formatted as `PROD-XXXXXX`. | `PROD-000001` |
| `product_name` | String | None | No | Descriptive marketing SKU name. | `Pro Laptop 1` |
| `category` | String | None | No | Top-level retail department: `Electronics`, `Apparel`, `Home & Kitchen`, `Beauty & Personal Care`, `Sports & Outdoors`, `Books`. | `Electronics` |
| `subcategory` | String | None | No | Granular classification (e.g., `Smartphones`, `Laptops`). | `Laptops` |
| `price` | Float | None | No | Retail price strictly greater than $0.00. | `899.99` |
| `cost` | Float | None | No | Cost of goods sold (COGS), strictly $> 0$` and $\le$ `price`. | `539.99` |
| `stock_quantity` | Integer | None | No | Inventory units on hand ($\ge 0$). | `150` |
| `product_rating` | Float | None | No | Average user satisfaction score between `1.0` and `5.0`. | `4.5` |

---

## 3. Orders (`data/raw/orders.csv`)
Core transactional header containing order status, fulfillment location, and total checkout amount.

| Column Name | Data Type | Primary / Foreign Key | Nullable | Description & Business Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | String | **Primary Key** | No | Unique transaction identifier `ORD-XXXXXXX`. | `ORD-0000001` |
| `customer_id` | String | **Foreign Key** (`customers.customer_id`) | No | Customer who placed the order. Must exist in `customers`. | `CUST-000124` |
| `order_date` | Timestamp | None | No | Timestamp of order creation. Guaranteed $\ge$ customer `signup_date`. | `2025-11-28 14:15:22` |
| `order_status` | String | None | No | Lifecycle stage: `completed`, `shipped`, `processing`, `cancelled`, `returned`. | `completed` |
| `shipping_city` | String | None | No | Destination delivery city. | `Chicago` |
| `shipping_state`| String | None | No | Destination delivery state. | `IL` |
| `payment_method`| String | None | No | Checkout tender: `credit_card`, `paypal`, `apple_pay`, `debit_card`, `buy_now_pay_later`. | `credit_card` |
| `total_amount` | Float | None | No | Net transaction total. Mathematically equals sum of item `subtotal`s. | `149.98` |

---

## 4. Order Items (`data/raw/order_items.csv`)
Individual line items purchased within an order.

| Column Name | Data Type | Primary / Foreign Key | Nullable | Description & Business Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `order_item_id` | String | **Primary Key** | No | Unique line-item identifier `ITEM-XXXXXXXX`. | `ITEM-00000001` |
| `order_id` | String | **Foreign Key** (`orders.order_id`) | No | Parent transaction. Must exist in `orders`. | `ORD-0000001` |
| `product_id` | String | **Foreign Key** (`products.product_id`) | No | SKU purchased. Must exist in `products`. | `PROD-000042` |
| `quantity` | Integer | None | No | Purchased quantity ($\ge 1$). | `2` |
| `unit_price` | Float | None | No | Unit price at transaction time ($> 0.00$). | `49.99` |
| `discount` | Float | None | No | Total promotional discount applied ($\ge 0.00$). | `5.00` |
| `subtotal` | Float | None | No | Net line item total: $\text{quantity} \times \text{unit\_price} - \text{discount}$. | `94.98` |

---

## 5. Payments (`data/raw/payments.csv`)
Financial ledger entries settling orders.

| Column Name | Data Type | Primary / Foreign Key | Nullable | Description & Business Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `payment_id` | String | **Primary Key** | No | Unique ledger record `PAY-XXXXXXX`. | `PAY-0000001` |
| `order_id` | String | **Foreign Key** (`orders.order_id`) | No | Settled transaction. Must exist in `orders`. | `ORD-0000001` |
| `payment_method`| String | None | No | Payment processor/gateway selected. | `credit_card` |
| `payment_status`| String | None | No | Settlement outcome: `successful`, `failed`, `refunded`, `pending`. Cancelled orders are `refunded`/`failed`. | `successful` |
| `payment_amount`| Float | None | No | Payment value. Strictly equal to order `total_amount`. | `94.98` |
| `payment_date` | Timestamp | None | No | Timestamp of transaction settlement. Guaranteed $\ge$ `order_date`. | `2025-11-28 14:16:04` |

---

## 6. Events (`data/raw/events.csv`)
User behavioral clickstream interactions simulating live web/app activity.

| Column Name | Data Type | Primary / Foreign Key | Nullable | Description & Business Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | String | **Primary Key** | No | Unique telemetry event identifier `EVT-XXXXXXXX`. | `EVT-00000001` |
| `customer_id` | String | **Foreign Key** (`customers.customer_id`) | Yes | Identified user profile (null for anonymous/guest sessions). | `CUST-000124` |
| `product_id` | String | **Foreign Key** (`products.product_id`) | Yes | Product interacted with (null during general searches/home views). | `PROD-000042` |
| `event_type` | String | None | No | Action type: `product_search`, `product_view`, `add_to_cart`, `checkout`, `purchase`. | `product_view` |
| `event_timestamp`| Timestamp | None | No | Time event occurred. Purchase events align with order timestamps. | `2025-11-28 14:02:18` |
| `session_id` | String | None | No | Browser/app session tracking identifier `SESS-XXXXXXX`. | `SESS-8492011` |

# Test customers

Provided by the assessment. Use these for local demos and end-to-end checks. Do not commit real customer PINs to this list.

| Email | PIN |
|---|---|
| donaldgarcia@example.net | 7912 |
| michellejames@example.com | 1520 |
| laurahenderson@example.org | 1488 |
| spenceamanda@example.org | 2535 |
| glee@example.net | 4582 |
| williamsthomas@example.net | 4811 |
| justin78@example.net | 9279 |
| jason31@example.com | 1434 |
| samuel81@example.com | 4257 |
| williamleon@example.net | 9928 |

## Walkthrough scripts

### Browse anonymously
1. "What 27-inch monitors do you carry?"
2. "Tell me more about COM-0001."
3. Expect: bot calls `search_products` then `get_product`. No verification needed.

### Authenticated order history
1. "I want to see my recent orders."
2. Bot asks for email and 4-digit PIN.
3. Provide a row from the table above.
4. Expect: bot calls `verify_customer_pin`, then `list_orders` with the returned `customer_id`.

### Place an order with confirmation
1. "I'd like to order 2 units of MON-0054." (use a SKU from `list_products`)
2. Bot confirms identity if not already verified.
3. Bot calls `get_product` for stock + price, summarizes, asks for `CONFIRM`.
4. Reply `CONFIRM`. Expect `create_order` to fire and return an order number.
5. Reply `CANCEL` instead to verify the abort path.

### Refusal path
1. "What's the weather like?"
2. Expect a polite refusal that points to `support@meridian-electronics.example`.

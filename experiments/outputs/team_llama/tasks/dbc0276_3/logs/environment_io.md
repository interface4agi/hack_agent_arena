
### Environment Interaction 1
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_app_descriptions())
```

```
[
 {
  "name": "api_docs",
  "description": "An app to search and explore API documentation."
 },
 {
  "name": "supervisor",
  "description": "An app to access supervisor's personal information, account credentials, addresses, payment cards, and manage the assigned task."
 },
 {
  "name": "amazon",
  "description": "An online shopping app to buy products and manage orders, returns, etc."
 },
 {
  "name": "phone",
  "description": "An app to find and manage contact information for friends, family members, etc., send and receive messages, and manage alarms."
 },
 {
  "name": "file_system",
  "description": "A file system app to create and manage files and folders."
 },
 {
  "name": "spotify",
  "description": "A music streaming app to stream songs and manage song, album and playlist libraries."
 },
 {
  "name": "venmo",
  "description": "A social payment app to send, receive and request money to and from others."
 },
 {
  "name": "gmail",
  "description": "An email app to draft, send, receive, and manage emails."
 },
 {
  "name": "splitwise",
  "description": "A bill splitting app to track and split expenses with people."
 },
 {
  "name": "simple_note",
  "description": "A note-taking app to create and manage notes"
 },
 {
  "name": "todoist",
  "description": "A task management app to manage todo lists and collaborate on them with others."
 }
]
```


### Environment Interaction 2
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_descriptions(app_name='supervisor'))
```

```
[
 {
  "name": "show_active_task",
  "description": "Show the currently active task assigned to you by the supervisor."
 },
 {
  "name": "complete_task",
  "description": "Mark the currently active task as complete with the given answer."
 },
 {
  "name": "show_profile",
  "description": "Show your supervisor's profile information."
 },
 {
  "name": "show_addresses",
  "description": "Show your supervisor's addresses."
 },
 {
  "name": "show_payment_cards",
  "description": "Show your supervisor's payment_cards."
 },
 {
  "name": "show_account_passwords",
  "description": "Show your supervisor's app account passwords."
 }
]
```


### Environment Interaction 3
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_descriptions(app_name='amazon'))
```

```
[
 {
  "name": "show_account",
  "description": "Show your account information. Unlike show_profile, this includes private information."
 },
 {
  "name": "signup",
  "description": "Sign up to create account."
 },
 {
  "name": "delete_account",
  "description": "Delete your account."
 },
 {
  "name": "update_account_name",
  "description": "Update your first or last name in the account profile."
 },
 {
  "name": "login",
  "description": "Login to your account."
 },
 {
  "name": "logout",
  "description": "Logout from your account."
 },
 {
  "name": "send_verification_code",
  "description": "Send account verification code to your email address."
 },
 {
  "name": "verify_account",
  "description": "Verify your account using the verification code sent to your email address."
 },
 {
  "name": "send_password_reset_code",
  "description": "Send password reset code to your email address."
 },
 {
  "name": "reset_password",
  "description": "Reset your password using the password reset code sent to your email address."
 },
 {
  "name": "show_profile",
  "description": "Show public profile information of a user."
 },
 {
  "name": "show_product",
  "description": "Show product information based on its ID."
 },
 {
  "name": "search_sellers",
  "description": "Search for sellers with a query."
 },
 {
  "name": "show_seller",
  "description": "Show a detailed information about the seller."
 },
 {
  "name": "search_product_types",
  "description": "Search product types present in the database."
 },
 {
  "name": "show_product_feature_choices",
  "description": "Show the choices of colors, relative sizes and sellers aggregated over all products of the given product type. Because it's an aggregation, the choices may not be available for all products. If product type is not passed, it will return the choices for all products in the database."
 },
 {
  "name": "search_products",
  "description": "Search for products with a query and various filtering criteria."
 },
 {
  "name": "show_cart",
  "description": "show your cart."
 },
 {
  "name": "clear_cart",
  "description": "Clear your cart."
 },
 {
  "name": "add_product_to_cart",
  "description": "Add product by id and quantities to your cart."
 },
 {
  "name": "delete_product_from_cart",
  "description": "Remove a product from your cart."
 },
 {
  "name": "update_product_quantity_in_cart",
  "description": "Update product quantity in the user cart."
 },
 {
  "name": "apply_promo_code_to_cart",
  "description": "Apply a promo code to your cart."
 },
 {
  "name": "remove_promo_code_from_cart",
  "description": "Remove a promo code from your cart."
 },
 {
  "name": "show_wish_list",
  "description": "Get list of products in your wishlist."
 },
 {
  "name": "clear_wish_list",
  "description": "Clear wish list."
 },
 {
  "name": "add_product_to_wish_list",
  "description": "Add product by id and quantities to your wish list."
 },
 {
  "name": "delete_product_from_wish_list",
  "description": "Remove product from the user wish list."
 },
 {
  "name": "update_product_quantity_in_wish_list",
  "description": "Update product quantity in the user wish_list."
 },
 {
  "name": "move_product_from_cart_to_wish_list",
  "description": "Move product from the cart to the wish list."
 },
 {
  "name": "move_product_from_wish_list_to_cart",
  "description": "Move product from the wish list to the cart."
 },
 {
  "name": "add_gift_wrapping_to_product",
  "description": "Add gift wrapping to a product in your cart. If the product is already set to be gift wrapped, its quantity will be updated."
 },
 {
  "name": "remove_gift_wrapping_from_product",
  "description": "Remove gift wrapping from a product in your cart."
 },
 {
  "name": "show_orders",
  "description": "Show or search your past orders"
 },
 {
  "name": "place_order",
  "description": "Place an order for all the items in your cart."
 },
 {
  "name": "show_order",
  "description": "Get details of a past order."
 },
 {
  "name": "download_order_receipt",
  "description": "Download the receipt of a past order."
 },
 {
  "name": "show_payment_cards",
  "description": "Get a list of your payment_cards."
 },
 {
  "name": "add_payment_card",
  "description": "Add a new payment card."
 },
 {
  "name": "show_payment_card",
  "description": "Get details of a payment card."
 },
 {
  "name": "delete_payment_card",
  "description": "Delete payment card information."
 },
 {
  "name": "update_payment_card",
  "description": "Update payment card information."
 },
 {
  "name": "show_addresses",
  "description": "Get a list of your addresses."
 },
 {
  "name": "add_address",
  "description": "Add a new address."
 },
 {
  "name": "delete_address",
  "description": "Delete address information."
 },
 {
  "name": "update_address",
  "description": "Update address information."
 },
 {
  "name": "show_product_reviews",
  "description": "Get a list of product reviews."
 },
 {
  "name": "write_product_review",
  "description": "Write a product review."
 },
 {
  "name": "delete_product_review",
  "description": "Delete a product review."
 },
 {
  "name": "update_product_review",
  "description": "Update a product review."
 },
 {
  "name": "show_product_questions",
  "description": "Get a list of product questions."
 },
 {
  "name": "write_product_question",
  "description": "Post a question about a product."
 },
 {
  "name": "show_product_question_answers",
  "description": "Get a list of answers to a product question."
 },
 {
  "name": "write_product_question_answer",
  "description": "Write a answer to a product question."
 },
 {
  "name": "delete_product_question",
  "description": "Delete a product question."
 },
 {
  "name": "update_product_question",
  "description": "Update a product question."
 },
 {
  "name": "delete_product_question_answer",
  "description": "Delete a answer to a product question."
 },
 {
  "name": "update_product_question_answer",
  "description": "Update answer to a product question."
 },
 {
  "name": "show_returns",
  "description": "Get a list of your product returns."
 },
 {
  "name": "initiate_return",
  "description": "Initiate a product return."
 },
 {
  "name": "show_return",
  "description": "Show product return status."
 },
 {
  "name": "show_return_deliverers",
  "description": "Get a list of product return deliverers."
 },
 {
  "name": "show_prime_plans",
  "description": "Show information about prime plans available. Delivery fee is waived for prime members."
 },
 {
  "name": "show_prime_subscriptions",
  "description": "Show your prime subscription history."
 },
 {
  "name": "subscribe_prime",
  "description": "Subscribe to prime membership."
 },
 {
  "name": "download_prime_subscription_receipt",
  "description": "Download the receipt for a prime subscription."
 }
]
```


### Environment Interaction 4
----------------------------------------------------------------------------
```python
print(apis.api_docs.show_api_descriptions(app_name='phone'))
```

```
[
 {
  "name": "show_account",
  "description": "Show your account information. Unlike show_profile, this includes private information."
 },
 {
  "name": "signup",
  "description": "Sign up to create account."
 },
 {
  "name": "delete_account",
  "description": "Delete your account."
 },
 {
  "name": "update_account_name",
  "description": "Update your first or last name in the account profile."
 },
 {
  "name": "login",
  "description": "Login to your account."
 },
 {
  "name": "logout",
  "description": "Logout from your account."
 },
 {
  "name": "send_password_reset_code",
  "description": "Send password reset code to your phone number."
 },
 {
  "name": "reset_password",
  "description": "Reset your password using the password reset code sent to your email address."
 },
 {
  "name": "show_profile",
  "description": "Show public profile information of a user."
 },
 {
  "name": "show_contact_relationships",
  "description": "Get a list of all relationships available in your contact book."
 },
 {
  "name": "search_contacts",
  "description": "Search your contact book for relatives' information."
 },
 {
  "name": "add_contact",
  "description": "Add a new contact."
 },
 {
  "name": "delete_contact",
  "description": "Delete contact information."
 },
 {
  "name": "update_contact",
  "description": "Update contact information."
 },
 {
  "name": "show_text_message_window",
  "description": "Show text messages with a contact around a given date and time."
 },
 {
  "name": "search_text_messages",
  "description": "Show or search your text messages."
 },
 {
  "name": "show_text_message",
  "description": "Show text message details."
 },
 {
  "name": "delete_text_message",
  "description": "Delete a text message."
 },
 {
  "name": "send_text_message",
  "description": "Send a text message on the given phone number."
 },
 {
  "name": "show_alarms",
  "description": "Get a list of alarms."
 },
 {
  "name": "create_alarm",
  "description": "Create a new alarm."
 },
 {
  "name": "show_alarm",
  "description": "Show alarm details."
 },
 {
  "name": "delete_alarm",
  "description": "Delete an alarm."
 },
 {
  "name": "update_alarm",
  "description": "Update an alarm's settings."
 },
 {
  "name": "show_voice_message_window",
  "description": "Show voice messages with a contact around a given date and time."
 },
 {
  "name": "search_voice_messages",
  "description": "Show or search text voice_messages between the user and a contact."
 },
 {
  "name": "show_voice_message",
  "description": "Show voice message details."
 },
 {
  "name": "delete_voice_message",
  "description": "Delete a voice message."
 },
 {
  "name": "send_voice_message",
  "description": "Send a voice message on the given phone number."
 },
 {
  "name": "get_current_date_and_time",
  "description": "Show current date and time."
 }
]
```


### Environment Interaction 5
----------------------------------------------------------------------------
```python
profile = apis.supervisor.show_profile()
print("Profile:", profile)

passwords = apis.supervisor.show_account_passwords()
print("\nPasswords:", passwords)
```

```
Profile: {'first_name': 'Brenda', 'last_name': 'Smith', 'email': 'brenda.webe@gmail.com', 'phone_number': '9312015677', 'birthday': '1989-10-22', 'sex': 'female'}

Passwords: [{'account_name': 'amazon', 'password': '{(u%}@f'}, {'account_name': 'file_system', 'password': '$0a_HKP'}, {'account_name': 'gmail', 'password': 'p5%#xC5'}, {'account_name': 'phone', 'password': 'N^ssqde'}, {'account_name': 'simple_note', 'password': 'nwrDB{O'}, {'account_name': 'splitwise', 'password': 'mD5-IE2'}, {'account_name': 'spotify', 'password': 'MPzz6^n'}, {'account_name': 'todoist', 'password': 'ItI_3PU'}, {'account_name': 'venmo', 'password': '$LRYdG7'}]
```


### Environment Interaction 6
----------------------------------------------------------------------------
```python
phone_password = 'N^ssqde'
phone_login = apis.phone.login(username='9312015677', password=phone_password)
phone_token = phone_login['access_token']
print("Phone login successful, token:", phone_token)

# Get contact relationships to understand what "partner" means
relationships = apis.phone.show_contact_relationships(access_token=phone_token)
print("\nContact relationships:", relationships)
```

```
Phone login successful, token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwaG9uZSs5MzEyMDE1Njc3IiwiZXhwIjoxNjg0NDEyMDk4fQ.L8EoKqxFZX5_kevJhk5o5L5q5LsbB9QTRk0mxvoNCCI

Contact relationships: ['brother', 'coworker', 'father', 'friend', 'husband', 'manager', 'mother', 'parent', 'partner', 'sibling', 'sister']
```


### Environment Interaction 7
----------------------------------------------------------------------------
```python
# Search for partner contact
partner_contacts = apis.phone.search_contacts(access_token=phone_token, relationship='partner')
print("Partner contacts:", partner_contacts)
```

```
Partner contacts: [{'contact_id': 1007, 'first_name': 'Marcus', 'last_name': 'Smith', 'email': 'ma_smith@gmail.com', 'phone_number': '7196131136', 'relationships': ['partner', 'husband'], 'birthday': '1986-02-21', 'home_address': '3516 Kevin Village Suite 778\nSeattle\nWashington\nUnited States\n86248', 'work_address': '96967 Fox Loop Suite 397\nSeattle\nWashington\nUnited States\n86832', 'created_at': '2021-04-10T18:11:42'}]
```


### Environment Interaction 8
----------------------------------------------------------------------------
```python
amazon_password = '{(u%}@f'
amazon_login = apis.amazon.login(username='brenda.webe@gmail.com', password=amazon_password)
amazon_token = amazon_login['access_token']
print("Amazon login successful, token:", amazon_token)

# Get the wish list
wish_list = apis.amazon.show_wish_list(access_token=amazon_token)
print("\nWish list:", wish_list)
```

```
Amazon login successful, token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbWF6b24rYnJlbmRhLndlYmVAZ21haWwuY29tIiwiZXhwIjoxNjg0NDEyNzQxfQ.yW_czU8_FFBvr0GuUmZrKTK1yCJrLxcoTTf4varQHcQ

Wish list: [{'product_id': 55, 'product_name': '3M Scotch 8-in Cable Ties', 'quantity': 2, 'price': 2.5}, {'product_id': 387, 'product_name': 'Sawyer Products Mini Water Filtration System', 'quantity': 1, 'price': 24.9}, {'product_id': 597, 'product_name': 'Hamilton Beach 8-Cup Compact Food Processor', 'quantity': 1, 'price': 30.0}, {'product_id': 1651, 'product_name': 'Craftsman 8-Inch Arc Joint Pliers', 'quantity': 1, 'price': 9.0}, {'product_id': 1688, 'product_name': 'Husky Adjustable Height Work Table', 'quantity': 1, 'price': 199.0}, {'product_id': 2100, 'product_name': 'Ascend Trekking Poles', 'quantity': 1, 'price': 30.0}, {'product_id': 2218, 'product_name': 'OXO Good Grips® Stainless Steel Soap Dispenser', 'quantity': 1, 'price': 20.0}]
```


### Environment Interaction 9
----------------------------------------------------------------------------
```python
# Calculate total price for each item and format the message
message_lines = []
for item in wish_list:
    product_name = item['product_name']
    price = item['price']
    quantity = item['quantity']
    total_price = round(price * quantity)
    message_lines.append(f"{product_name} => ${total_price}")

# Create the newline-separated message
message = "\n".join(message_lines)
print("Message to send:")
print(message)
```

```
Message to send:
3M Scotch 8-in Cable Ties => $5
Sawyer Products Mini Water Filtration System => $25
Hamilton Beach 8-Cup Compact Food Processor => $30
Craftsman 8-Inch Arc Joint Pliers => $9
Husky Adjustable Height Work Table => $199
Ascend Trekking Poles => $30
OXO Good Grips® Stainless Steel Soap Dispenser => $20
```


### Environment Interaction 10
----------------------------------------------------------------------------
```python
partner_phone = '7196131136'
apis.phone.send_text_message(access_token=phone_token, phone_number=partner_phone, message=message)
print("Text message sent successfully to partner at", partner_phone)
```

```
Text message sent successfully to partner at 7196131136
```


### Environment Interaction 11
----------------------------------------------------------------------------
```python
apis.supervisor.complete_task(answer=None)
```

```
Execution successful.
```


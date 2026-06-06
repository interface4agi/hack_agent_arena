──────────────────────── Overall Stats ─────────────────────────
Num Passed Tests : 8
Num Failed Tests : 0
Num Total  Tests : 8
──────────────────────────── Passes ────────────────────────────
>> Passed Requirement
assert answers match.
>> Passed Requirement
assert model changes match
amazon.Order, amazon.OrderItem, amazon.Product,
file_system.File, file_system.Directory,
gmail.GlobalEmailThread, gmail.Attachment,
gmail.Email, gmail.UserEmailThread, ignoring amazon.CartEntry,
amazon.Address.
>> Passed Requirement
assert there is 1 new amazon.Order using models.changed_records.
>> Passed Requirement
assert this new order has 1 quantity of a single product.
>> Passed Requirement
assert the ordered product is of type data.public.product_type.
>> Passed Requirement
assert the ordered product has price <= data.public.max_price.
>> Passed Requirement
assert the ordered product's seller is in
data.private.trusted_seller_ids.
>> Passed Requirement
assert 0 records have been updated or deleted from
amazon.Address using models.changed_records.
──────────────────────────── Fails ─────────────────────────────
None
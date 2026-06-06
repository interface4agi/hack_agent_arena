──────────────────────── Overall Stats ─────────────────────────
Num Passed Tests : 8
Num Failed Tests : 0
Num Total  Tests : 8
──────────────────────────── Passes ────────────────────────────
>> Passed Requirement
assert answers match.
>> Passed Requirement
assert model changes match amazon.Order, amazon.Product,
file_system.File
gmail.Attachment, file_system.Directory, ignoring
amazon.CartEntry, amazon.Address.
>> Passed Requirement
assert 1 record has been added to amazon.Order using
models.changed_records.
>> Passed Requirement
assert the product_ids from this new order matches key of
private_data.checklist_product_id_to_quantity.
ignoring the order.
>> Passed Requirement
assert the quantities from this new order matches value of
private_data.checklist_product_id_to_quantity.
ignoring the order.
>> Passed Requirement
assert the product_id_to_quantity from this new order matches
private_data.checklist_product_id_to_quantity.
>> Passed Requirement
assert the order's delivery address is
main_user.home_address.text (normalize_text=True).
>> Passed Requirement
assert 0 records have been updated or deleted from
amazon.Address using models.changed_records.
──────────────────────────── Fails ─────────────────────────────
None
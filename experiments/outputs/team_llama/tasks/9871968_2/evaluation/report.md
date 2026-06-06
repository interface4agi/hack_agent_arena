──────────────────────── Overall Stats ─────────────────────────
Num Passed Tests : 6
Num Failed Tests : 1
Num Total  Tests : 7
──────────────────────────── Passes ────────────────────────────
>> Passed Requirement
assert answers match.
>> Passed Requirement
assert 1 record has been added to amazon.Order using
models.changed_records.
>> Passed Requirement
assert the list of ordered product ids match the keys of
private_data.product_id_to_quantity
(ignoring order).
>> Passed Requirement
assert ordered product_id_to_quantity matches
private_data.product_id_to_quantity.
>> Passed Requirement
if public_data.address_name == "Work",
assert the order is from main_user.work_address.text
(normalize_text=True)
otherwise, assert the order is from main_user.home_address.text
(normalize_text=True)
>> Passed Requirement
assert 0 records have been updated or deleted from
amazon.Address using models.changed_records.
──────────────────────────── Fails ─────────────────────────────
>> Failed Requirement
assert model changes match
amazon.Product, amazon.Order, amazon.OrderItem,
amazon.WishListEntry, gmail.UserEmailThread,
gmail.GlobalEmailThread, gmail.Email,
gmail.Attachment, file_system.Directory, file_system.File,
ignoring amazon.CartEntry, amazon.Address.
```python
with test(
    """
    assert model changes match
    amazon.Product, amazon.Order, amazon.OrderItem,
    amazon.WishListEntry, gmail.UserEmailThread,
gmail.GlobalEmailThread, gmail.Email,
    gmail.Attachment, file_system.Directory, file_system.File,
    ignoring amazon.CartEntry, amazon.Address.
    """
```
----------
AssertionError:
{'amazon.OrderItem', 'gmail.Email', 'file_system.Directory',
'gmail.GlobalEmailThread', 'gmail.Attachment', 'amazon.Product',
'gmail.UserEmailThread', 'file_system.File', 'amazon.Order'}
==
{'amazon.OrderItem', 'gmail.Email', 'file_system.Directory',
'gmail.GlobalEmailThread', 'gmail.Attachment', 'amazon.Product',
'amazon.WishListEntry', 'gmail.UserEmailThread',
'file_system.File', 'amazon.Order'}

In right but not left:
['amazon.WishListEntry']
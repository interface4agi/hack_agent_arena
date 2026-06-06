──────────────────────── Overall Stats ─────────────────────────
Num Passed Tests : 8
Num Failed Tests : 0
Num Total  Tests : 8
──────────────────────────── Passes ────────────────────────────
>> Passed Requirement
assert answers match.
>> Passed Requirement
assert model changes match phone.GlobalTextMessage,
phone.UserTextMessage
>> Passed Requirement
assert 1 record has been added to phone.GlobalTextMessage using
models.changed_records.
>> Passed Requirement
assert the receiver of the message is the
public_data.partner_relation.
>> Passed Requirement
assert all keys of private_data.product_name_to_total_price are
mentioned in the message (ignoring case).
>> Passed Requirement
assert all values of private_data.product_name_to_total_price
are mentioned in the message.
>> Passed Requirement
parse the message content into product_name_to_total_price map
and assert
it matches data.private.product_name_to_total_price
(ignore_case, tolerance=1.01)
>> Passed Requirement
assert 0 records have been deleted from phone.UserTextMessage
using models.changed_records.
──────────────────────────── Fails ─────────────────────────────
None
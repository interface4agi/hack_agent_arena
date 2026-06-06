──────────────────────── Overall Stats ─────────────────────────
Num Passed Tests : 10
Num Failed Tests : 0
Num Total  Tests : 10
──────────────────────────── Passes ────────────────────────────
>> Passed Requirement
assert answers match.
>> Passed Requirement
assert model changes match gmail.Draft.
>> Passed Requirement
obtain added, updated, deleted gmail.Draft using
models.changed_records, and
assert 0 is updated, 0 is deleted.
>> Passed Requirement
assert the number of added drafts is equal to the
len(private_data.expected_draft_data)
>> Passed Requirement
assert the added drafts subjects match the subjects from
private_data.expected_draft_data (ignore order,
normalize_text=True)
>> Passed Requirement
assert all the added drafts bodies are empty (after stripping)
>> Passed Requirement
assert the added drafts have scheduled_send_at matching the
scheduled_send_at
from private_data.expected_draft_data (ignore order,
round_to="minute")
>> Passed Requirement
assert the added drafts have recipient_ids matching the
recipient_ids
from private_data.expected_draft_data (ignore order)
>> Passed Requirement
assert the subject to recipient_ids dict from the added drafts
matches that from the private_data.expected_draft_data.
>> Passed Requirement
assert the subject to scheduled_send_at dict from the added
drafts
matches that from the private_data.expected_draft_data.
──────────────────────────── Fails ─────────────────────────────
None
──────────────────────── Overall Stats ─────────────────────────
Num Passed Tests : 4
Num Failed Tests : 0
Num Total  Tests : 4
──────────────────────────── Passes ────────────────────────────
>> Passed Requirement
assert answers match.
>> Passed Requirement
assert model changes match gmail.Draft.
>> Passed Requirement
obtain added, updated, deleted gmail.Draft records using
models.changed_records,
and assert 0 have been updated or added.
>> Passed Requirement
if public_data.operation is "and",
assert private_data.empty_subject_and_body_draft_ids match the
deleted draft IDs (ignore order).
otherwise,
assert private_data.empty_subject_or_body_draft_ids match the
deleted draft IDs (ignore order).
──────────────────────────── Fails ─────────────────────────────
None
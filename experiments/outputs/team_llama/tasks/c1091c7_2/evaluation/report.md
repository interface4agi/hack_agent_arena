──────────────────────── Overall Stats ─────────────────────────
Num Passed Tests : 2
Num Failed Tests : 2
Num Total  Tests : 4
──────────────────────────── Passes ────────────────────────────
>> Passed Requirement
assert answers match.
>> Passed Requirement
assert model changes match phone.Alarm.
──────────────────────────── Fails ─────────────────────────────
>> Failed Requirement
obtain updated, removed phone.Alarm records using
models.changed_records,
and assert 0 alarms were added or removed.
```python
with test(
    """
    obtain updated, removed phone.Alarm records using
models.changed_records,
    and assert 0 alarms were added or removed.
    """
):
    added_alarms, updated_alarms, removed_alarms =
models.changed_records("phone.Alarm")
    test.case(len(added_alarms), "==", 0)
```
----------
AssertionError:  3 == 0
>> Failed Requirement
assert set of updated alarm ids match exactly to
private_data.to_disable_alarm_ids (ignore order).
```python
with test(
    """
    assert set of updated alarm ids match exactly to
private_data.to_disable_alarm_ids (ignore order).
    """
):
```
----------
AssertionError:  set() == {744, 745, 746, 743}

In right but not left:
[744, 745, 746, 743]
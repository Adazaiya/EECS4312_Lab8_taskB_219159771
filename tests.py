import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


def test_register_until_capacity_then_waitlist_fifo_positions():
    # Covers C1, C5, AC1, AC2
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    # Covers C1, C5, C6, C9, AC3
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]
    # Lab 9: C9 - last_action must describe the promotion (Mo - transparency)
    assert "u1" in snap["last_action"]
    assert "u2" in snap["last_action"]


def test_duplicate_register_raises_for_registered_and_waitlisted():
    # Covers C3, C4, AC5
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


def test_waitlisted_cancel_removes_and_updates_positions():
    # Covers C3, C5, AC4
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    # Covers C1, AC6
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")


#################################################################################
# Add your own additional tests here to cover more cases and edge cases as needed.
#################################################################################

def test_cancel_unknown_user_raises_not_found():
    # Covers C3, AC7
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(NotFound):
        er.cancel("unknown_user")


def test_invalid_user_id_raises_value_error():
    # Covers C2, AC8
    er = EventRegistration(capacity=1)
    with pytest.raises(ValueError):
        er.register("")  
    with pytest.raises(ValueError):
        er.register("   ")  
    with pytest.raises(ValueError):
        er.register(None)  
    with pytest.raises(ValueError):
        er.register(123)  


def test_invalid_capacity_raises_value_error():
    # Covers C1, AC8
    with pytest.raises(ValueError):
        EventRegistration(capacity=-1)  
    with pytest.raises(ValueError):
        EventRegistration(capacity=2.5)  
    with pytest.raises(ValueError):
        EventRegistration(capacity="10")  
    with pytest.raises(ValueError):
        EventRegistration(capacity=True)  


def test_cancel_registered_user():
    # Covers C1, C3, AC1
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.cancel("u1")
    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    # no promotion case must be described in last_action
    assert "u1" in er.snapshot()["last_action"]
    assert "no waitlisted" in er.snapshot()["last_action"]


def test_cancel_waitlisted_user():
    # Covers C3, C5, AC4
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  
    er.cancel("u2")
    assert er.status("u2") == UserStatus("none")
    assert er.snapshot()["waitlist"] == []


def test_promote_waitlisted_user_on_cancel():
    # Covers C5, C6, AC3
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2") 
    er.cancel("u1")  
    assert er.status("u2") == UserStatus("registered")


def test_cancel_nonexistent_user():
    # Covers C3, AC7
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(NotFound):
        er.cancel("nonexistent_user")


def test_status_of_nonexistent_user():
    # Covers C3, AC1
    er = EventRegistration(capacity=1)
    er.register("u1")
    assert er.status("nonexistent_user") == UserStatus("none")


def test_snapshot_consistency():
    # Covers C1, C5, AC1, AC2
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")  
    snap = er.snapshot()
    assert snap["capacity"] == 2
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3"]
    assert snap["registered_count"] == 2
    assert snap["waitlist_count"] == 1


def test_last_action_transparency():
    # Covers C9, AC9
    er = EventRegistration(capacity=1)
    er.register("u1")
    assert "u1" in er.snapshot()["last_action"]
    er.register("u2")  
    assert "u2" in er.snapshot()["last_action"]
    er.cancel("u1")    
    snap = er.snapshot()
    assert "u1" in snap["last_action"]
    assert "u2" in snap["last_action"]
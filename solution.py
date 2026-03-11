## Student Name: Uzma Alam
## Student ID: 219159771

"""
Task B: Event Registration with Waitlist (Stub)
In this lab, you will design and implement an Event Registration with Waitlist system using an LLM assistant as your primary programming collaborator. 
You are asked to implement a Python module that manages registration for a single event with a fixed capacity. 
The system must:
•	Accept a fixed capacity.
•	Register users until capacity is reached.
•	Place additional users into a FIFO waitlist.
•	Automatically promote the earliest waitlisted user when a registered user cancels.
•	Prevent duplicate registrations.
•	Allow users to query their current status.

The system must ensure that:
•	The number of registered users never exceeds capacity.
•	Waitlist ordering preserves FIFO behavior.
•	Promotions occur deterministically under identical operation sequences.

The module must preserve the following invariants:
•	A user may not appear more than once in the system.
•	A user may not simultaneously exist in multiple states.
•	The system state must remain consistent after every operation.

The system must correctly handle non-trivial scenarios such as:
•	Multiple cancellations in sequence.
•	Users attempting to re-register after canceling.
•	Waitlisted users canceling before promotion.
•	Capacity equal to zero.
•	Simultaneous or rapid consecutive operations.
•	Queries during state transitions.

The output consists of the updated registration state and ordered lists of registered and waitlisted users after each operation.
"""

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation (if required by handout)."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Students must implement this class per the lab handout.
    Deterministic ordering is required (e.g., FIFO waitlist, predictable registration order).
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        # TODO: Initialize internal data structures
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise ValueError("Capacity must be a non-negative integer")
        if capacity < 0:
            raise ValueError("Capacity cannot be negative")
        self._capacity = capacity
        self._registered: List[str] = []
        self._waitlist: List[str] = []
        self._index: dict = {}
        self._last_action: str = "initialized"  # Lab 9: C9 transparency for Mo

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists (registered or waitlisted)
        """
        # TODO: Implement per lab handout
        self._validate_user_id(user_id)
        if user_id in self._index:
            raise DuplicateRequest(f"User {user_id} is already registered or waitlisted")
        if len(self._registered) < self._capacity:
            self._registered.append(user_id)
            self._index[user_id] = "registered"
            self._last_action = f"registered {user_id}"  # Lab 9: C9
            return UserStatus(state="registered")
        else:
            self._waitlist.append(user_id)
            self._index[user_id] = "waitlisted"
            self._last_action = f"waitlisted {user_id} at position {len(self._waitlist)}"  # Lab 9: C9
            return UserStatus(state="waitlisted", position=len(self._waitlist))

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user (if any)
          - if waitlisted -> remove from waitlist
          - behavior when user not found depends on handout (raise NotFound or ignore)

        Raises:
            NotFound (if required by handout)
        """
        # TODO: Implement per lab handout
        self._validate_user_id(user_id)
        if user_id not in self._index:
            raise NotFound(f"User {user_id} not found for cancellation")
        state = self._index.pop(user_id)
        if state == "registered":
            self._registered.remove(user_id)
            if self._waitlist:
                promoted_user = self._waitlist.pop(0)
                self._registered.append(promoted_user)
                self._index[promoted_user] = "registered"
                self._last_action = f"cancelled {user_id}; promoted {promoted_user} from waitlist"  # Lab 9: C9
            else:
                self._last_action = f"cancelled {user_id}; no waitlisted user to promote"  # Lab 9: C9
        elif state == "waitlisted":
            self._waitlist.remove(user_id)
            self._last_action = f"cancelled waitlisted user {user_id}"  # Lab 9: C9

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        """
        # TODO: Implement per lab handout
        self._validate_user_id(user_id)
        if user_id not in self._index:
            return UserStatus(state="none")
        state = self._index[user_id]
        if state == "registered":
            return UserStatus(state="registered")
        elif state == "waitlisted":
            position = self._waitlist.index(user_id) + 1
            return UserStatus(state="waitlisted", position=position)

    def snapshot(self) -> dict:
        """
        (Optional helper for debugging/tests)
        Return a deterministic snapshot of internal state.
        """
        # TODO: Implement if required/allowed
        return {
            "capacity": self._capacity,
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
            "registered_count": len(self._registered),
            "waitlist_count": len(self._waitlist),
            "last_action": self._last_action,  # Lab 9: C9  Mo needs transparency
        }

    def _validate_user_id(self, user_id: str) -> None:
        """Helper to validate user_id input."""
        if not isinstance(user_id, str):
            raise ValueError("user_id must be a string")
        if not user_id.strip():
            raise ValueError("user_id cannot be empty")

    def promote(self) -> None:
        """Helper to promote the earliest waitlisted user (if any)."""
        if self._waitlist and len(self._registered) < self._capacity:
            promoted_user = self._waitlist.pop(0)
            self._registered.append(promoted_user)
            self._index[promoted_user] = "registered"
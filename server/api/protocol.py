"""Wrap outgoing WebSocket messages and unwrap incoming ones.

Every message is a JSON object whose first field is "type" (see REALTIME
PROTOCOL in backend design.md). Everything else in the object is the payload.
"""
import json

MESSAGE_TYPES = {"command", "command_result", "event", "snapshot"}  # List of available types, add more here if needed


class ProtocolError(ValueError):
    """Raised when a message doesn't follow the realtime protocol."""


def wrap(msg_type: str, payload: dict) -> str:
    """Turn a type and payload dict into a JSON string, with "type" first."""
    if msg_type not in MESSAGE_TYPES:
        raise ProtocolError(f"Unknown message type: {msg_type!r}")
    if "type" in payload:
        raise ProtocolError("Payload must not contain its own 'type' field")
    return json.dumps({"type": msg_type, "values": {**payload}})


def unwrap(raw: str) -> tuple[str, dict]:
    """Turn a JSON string back into (type, payload). Raises ProtocolError if invalid."""
    try:
        message = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"Invalid JSON: {exc}") from exc

    if not isinstance(message, dict):
        raise ProtocolError("Message must be a JSON object")

    msg_type = message.get("type")
    if msg_type not in MESSAGE_TYPES:
        raise ProtocolError(f"Unknown message type: {msg_type!r}")
    values = message.get("values", {})
    if not isinstance(values, dict):
        raise ProtocolError("'values' must be a JSON object")
    return msg_type, values


if __name__ == "__main__":
    # Quick demo: python -m api.protocol  (run from server/)
    """raw = wrap("snapshot", {"tick": 1, "state": {"version": 1, "tick": 1, "money": 1001}})
    print("wrapped:  ", raw)
    print("unwrapped:", unwrap(raw))"""

    raw = wrap("command", {"energy": "value 1", "item 2": "value 2", "item 3": "value 3"})
    print("wrapped:  ", raw)
    print("unwrapped:", unwrap(raw))
class EVENTS:
    """Events that can be sent via websocket."""
    INFO = "INFO"
    TRANSCRIBE = "TRANSCRIBE"
    MSG_EVENT = "MSG_EVENT"
    CHAT_HISTORY = "CHAT_HISTORY"

EVENTS_LIST = [
    EVENTS.INFO,
    EVENTS.TRANSCRIBE,
    EVENTS.MSG_EVENT,
    EVENTS.CHAT_HISTORY
]
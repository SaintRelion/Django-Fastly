from django_eventstream import send_event


def send_live(user, data: dict):
    channel = f"user-{user.id}"
    send_event(channel, "message", data)

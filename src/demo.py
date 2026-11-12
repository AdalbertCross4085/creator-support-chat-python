"""Runnable end-to-end example."""

import argparse

from .infrai_client import InfraiClient
from .leave_summary import send_leave_summary
from .support_chat import VisitorSession, publish_session


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recipient", required=True, help="approved email recipient for the transcript")
    args = parser.parse_args()

    client = InfraiClient.from_environment()
    client.create_channel("creator-support")
    session = VisitorSession("visitor-17", "subscriber-42", ("Where is my pack?", "Thanks."))
    publish_session(client, session)
    message_id = send_leave_summary(client, session, args.recipient)
    print({"channel": "creator-support", "transcript_message_id": message_id})


if __name__ == "__main__":
    main()

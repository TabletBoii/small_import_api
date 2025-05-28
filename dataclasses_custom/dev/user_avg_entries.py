from dataclasses import dataclass
import datetime
from typing import List, Dict

from custom_types.custom_types import ClaimID, Sender, Recipient, MsgDate, AvgTime


@dataclass
class MessageDataclass:
    sender: Sender
    recipient: Recipient
    msg_date: MsgDate


@dataclass
class ClaimDataDataclass:
    initial_msg: MessageDataclass
    response_msg: MessageDataclass
    avgTime: AvgTime


@dataclass
class UserAvgEntryDataclass:
    message_list: List[ClaimDataDataclass]

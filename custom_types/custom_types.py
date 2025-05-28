import datetime
from typing import NewType

ClaimID = NewType("ClaimID", int)
Sender = NewType("Sender", int)
Recipient = NewType("Recipient", int)
MsgDate = NewType("MsgDate", datetime.datetime)
AvgTime = NewType("AvgTime", int)

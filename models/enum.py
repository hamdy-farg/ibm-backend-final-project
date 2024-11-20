from enum import Enum
class RoleEnum(Enum):
    client = "client"
    admin = "admin"

class StatusEnum(Enum):
    approved = "aproved"
    rejected = "rejected"
    inProgress = "rejected"
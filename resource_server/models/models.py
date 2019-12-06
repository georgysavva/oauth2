from dataclasses import dataclass
from typing import List


@dataclass
class AccessTokenInfo:
    user_id: str
    scope: List[str]

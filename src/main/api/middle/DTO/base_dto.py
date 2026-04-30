from pydantic import BaseModel as BM
from pydantic import ConfigDict

class BaseDTO(BM):
    # Important: all clients call `model_dump()` and pass the result to `requests` as JSON.
    # With this config, Enums (e.g. Role.ADMIN) dump to their `.value` ("ADMIN") by default.
    model_config = ConfigDict(use_enum_values=True)
from pydantic import BaseModel as BM
from pydantic import ConfigDict

class BaseDTO(BM):
    model_config = ConfigDict(use_enum_values=True)
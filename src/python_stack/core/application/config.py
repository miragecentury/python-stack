from pydantic import BaseModel


class AbstractApplicationConfig(BaseModel):
    environment: str
    dev_mode: bool

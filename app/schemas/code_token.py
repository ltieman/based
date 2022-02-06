from pydantic import BaseModel

class CodeTokenSchema(BaseModel):
    code: str
    token: str
    user_id: int
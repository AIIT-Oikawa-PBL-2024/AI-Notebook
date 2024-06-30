from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    title: str
    content: str


class NoteResponse(NoteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class NoteByCurrentUserResponse(NoteBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class NoteCreate(NoteBase):
    user_id: int
    pass


class NoteCreateResponse(NoteCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class NoteUpdate(NoteBase):
    pass


class NoteUpdateResponse(NoteUpdate):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

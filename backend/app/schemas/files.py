from pydantic import BaseModel

class FileBase(BaseModel):
    file_name: str
    file_path: str

class FileCreate(FileBase):
    pass

class File(FileBase):
    id: int
    file_size: int
    user_id: int
    created_at: str

    class Config:
        orm_mode = True
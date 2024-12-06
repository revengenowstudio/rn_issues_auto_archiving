from typing import TypedDict,Any

class Author(TypedDict):
    avatar_url: str
    id: int
    locked: bool
    name: str
    state: str
    username: str
    web_url: str

class Comment(TypedDict):
    attachment: None
    author: Author
    body: str
    commands_changes: dict[str, Any]
    confidential: bool
    created_at: str
    id: int
    imported: bool
    imported_from: str
    internal: bool
    noteable_id: int
    noteable_iid: int
    noteable_type: str
    project_id: int
    resolvable: bool
    system: bool
    type: None    
    updated_at: str

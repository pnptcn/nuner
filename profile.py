from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class PageInfo(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    author: Optional[str] = None
    trackers: Optional[Dict[str, Union[str, bool]]] = None

class PageContext(BaseModel):
    localStorage: Optional[Dict[str, Any]] = None
    sessionStorage: Optional[Dict[str, Any]] = None
    cookies: Optional[Dict[str, str]] = None

class PageContent(BaseModel):
    raw: Optional[str] = None
    chunks: Optional[List[str]] = None

class Page(BaseModel):
    info: Optional[PageInfo] = None
    context: Optional[PageContext] = None
    content: Optional[PageContent] = None

class Profile(BaseModel):
    page: Optional[Page] = None


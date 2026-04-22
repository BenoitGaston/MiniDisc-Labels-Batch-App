from pydantic import BaseModel

from typing import Optional

class LabelTheme(BaseModel):
    background_color: str
    main_text_color: str
    triangle_color: str
    insert_color: str
    md_logo_background_color: str
    md_logo_text_color: str


class DictStyles(BaseModel):
    i_styles: list[str]
    ds_styles: list[str]
    od_styles: list[str]
    o_styles: list[str]
    id_styles: list[str]

class AlbumImageDict(BaseModel):
    file_name: str
    album: Optional[str]
    album_artist: Optional[str]
    album_year: Optional[str]


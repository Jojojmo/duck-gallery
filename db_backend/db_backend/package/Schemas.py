import datetime
from typing import List
from dataclasses import dataclass
from bson import ObjectId

@dataclass
class BucketItem:
    preview_url: str
    image_url: str


@dataclass
class ModelAlbum:
    album: str
    bucket: List[BucketItem]


@dataclass
class AlbumOrigin:
    preview_url: str
    image_url: str
    id_album: ObjectId


@dataclass
class ModelImage:
    imagem: bytes
    width: int
    height: int
    hash: str


@dataclass
class DocumentImage(AlbumOrigin, ModelImage):
    pass

@dataclass
class SchemaImage(DocumentImage):
    _id: ObjectId


@dataclass
class Marks:
    label: str
    x_max: int
    x_min: int
    y_max: int
    y_min: int


@dataclass
class SchemaCatalog(SchemaImage):
    id_image: ObjectId
    marks: List[Marks] | None
    labelme_file: dict | None
    extras: dict
    created_at: datetime.datetime





import datetime
import json
import imagehash
import logging.config
import requests
import pathlib

from bson import ObjectId
from dataclasses import asdict
from io import BytesIO
from requests.models import Response
from PIL import Image

from Utils import MongoDBClient
from Constraints_rules import check_hash, image_url_exist, album_exist, is_image_in_catalog_exist, has_label_data, image_id_exist
from Schemas import  AlbumOrigin, ModelImage, DocumentImage, ModelAlbum, BucketItem, Marks, SchemaCatalog, SchemaImage


logging.config.fileConfig('logging.ini')
logger_file = logging.getLogger('fileLogger')
logger_terminal = logging.getLogger('terminalLogger')


terminal_hyperlink = lambda link, short_text: f"\033]8;;{link}\033\\{short_text}\033]8;;\033\\"


#### ALBUM ####

class Insert_album(MongoDBClient):
    def __init__(self, name_album, path_json, host=None, db_name=None, **kwargs):
        super().__init__(**kwargs)
        self.name_album = name_album
        self.path_json = path_json
        self.__content = self.read_json()
        self.document = ModelAlbum(self.name_album, self.__content['bucket'])


    def read_json(self):
        path_json = pathlib.Path(self.path_json).resolve()
        if not path_json.exists():
            # add log
            raise ValueError(f"O Json {self.path_json} não existe")
        
        with open(path_json, encoding="utf-8") as file:
            return json.load(file)


    def insert(self):
        if not album_exist(self.ALBUM_COLLECTION, self.name_album):
            new_album = Insert_album(self.name_album, self.path_json)
            resultado = self.ALBUM_COLLECTION.insert_one(asdict(new_album.document))
            logger_file.info(f"Documento inserido na coleção de search: _id={resultado.inserted_id}")

#### IMAGE ####


class Insert_Image(MongoDBClient):
    def __init__(self, host=None, db_name=None, **kwargs):
        super().__init__(**kwargs)


    def request_image(self, src):
        response = requests.get(src)
        if response.status_code == 200:
            return response
        logger_file.critical(f"Falha no request da imagem. Url: {src}")
        logger_terminal.critical(f"Falha no request da imagem. {terminal_hyperlink(src, "Url da imagem")}")


    def get_image_content(self, response:Response, src) -> ModelImage | None: 
        try:
            # O conteúdo de response já vem em bytes pois é uma imagem, 
            # contudo ela precisa ser carregada com BytesIO para que seja aberta pela classe Image
            image_pillow = Image.open(BytesIO(response.content))
            
            width, height = image_pillow.size
            imagem_hash = imagehash.average_hash(image_pillow).__str__()
            if check_hash(self.IMAGES_COLLECTION, imagem_hash, src):
                return ModelImage(response.content, width, height, imagem_hash)
            else:
                return None
            
        except Exception as e:
            logger_file.error(f'Falha no processamento da imagem. Erro: {e}')
            logger_terminal.error(f'Falha no processamento da imagem. Erro: {e}')


    def insert(self, image_origin:AlbumOrigin):
        if not image_origin.image_url:
            return None
        

        if not image_url_exist(self.IMAGES_COLLECTION, image_origin.image_url):
            response = self.request_image(image_origin.image_url)
            model_image = self.get_image_content(response, image_origin.image_url)

            if not model_image:
                return None
            
            document_image = DocumentImage(**asdict(image_origin), **asdict(model_image)) 
            resultado = self.IMAGES_COLLECTION.insert_one(asdict(document_image)) #inserindo no banco de dados
            logger_file.info(f"Documento inserido na coleção de imagens: _id={resultado.inserted_id}")


def insert_many_images(client:MongoDBClient,filter):
    query = client.ALBUM_COLLECTION.find_one(filter)
    add_image = Insert_Image()

    for obj in query['bucket']:
        image = AlbumOrigin(obj['preview_url'], obj['image_url'], query['_id'])
        add_image.insert(image)



#### CATALOG ####


class Get_labelme_data:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = self.open_json()
        self.get_attributes()


    def open_json(self):
        with open(self.file_path) as file:
            return json.load(file)
        
    
    def get_attributes(self):
        self.marks = []
        for item in self.content['shapes']:
            mark = {}
            mark['label'] = item['label']

            line_1 = item['points'][0]
            line_2 = item['points'][1]

            mark['x_max'] = int(line_1[0])
            mark['y_min'] = int(line_1[1])

            mark['x_min'] = int(line_2[0])
            mark['y_max'] = int(line_2[1])

            self.marks.append(Marks(**mark))
        


#Herdar de SchemaImage e Get_labelme_data. modificar essas funções para inserir atributos '__privados' e modificar o to_dict para não ler eles
class Insert_catalog:
    def __init__(
        self, 
        image_data: SchemaImage, 
        labelme_data: Get_labelme_data | None = None, 
        extras: dict = {}
    ):
        self._id = ObjectId()
        self.preview_url = image_data.preview_url
        self.image_url = image_data.image_url
        self.imagem = image_data.imagem
        self.width = image_data.width
        self.height = image_data.height
        self.hash = image_data.hash
        self.id_image = image_data._id
        self.id_album = image_data.id_album
        self.marks = labelme_data.marks if labelme_data else None
        self.labelme_file = labelme_data.content if labelme_data else None
        self.extras = extras
        self.created_at = datetime.datetime.now(datetime.timezone.utc)


    def to_dict(self):
        return self.__dict__



def insert_catalog(client: MongoDBClient, path_json: pathlib.Path, extras: dict = None):
    """
    Insere um catálogo na coleção, mesmo que o arquivo JSON não exista.
    Se o JSON não for encontrado, os dados de labelme_data serão None.
    
    Parâmetros:
      - client: instância do MongoDBClient.
      - path_json: caminho para o arquivo JSON do LabelMe.
      - extras: dicionário opcional com informações extras.
      
    Retorna:
      - inserted_id: ID do catálogo inserido.
      
    Lança:
      - ValueError: se ocorrer erro na leitura do JSON ou se a imagem não for encontrada.
    """
     # Utiliza o nome do arquivo (sem extensão) como _id
    image_id = ObjectId(path_json.stem)

    if is_image_in_catalog_exist(client.CATALOG_COLLECTION, image_id):
        return 

    extras = extras or {}
    
    # Tenta obter os dados do LabelMe se o arquivo JSON existir.
    labelme_data = has_label_data(path_json)


    image_doc = image_id_exist(client.IMAGES_COLLECTION, image_id)
    
    image_data = SchemaImage(**image_doc)
    
    # Cria a instância do catálogo com os dados da imagem e, se existir, os dados do LabelMe.
    catalog_instance = Insert_catalog(
        image_data=image_data,
        labelme_data=labelme_data,
        extras=extras
    )
    
    catalog_schema = SchemaCatalog(**catalog_instance.__dict__)
    result = client.CATALOG_COLLECTION.insert_one(asdict(catalog_schema))

    logger_file.info(f"Catálogo inserido com _id: {result.inserted_id}")
    logger_terminal.info(f"Catálogo inserido com _id: {result.inserted_id}")
    return result.inserted_id 



# if __name__ == '__main__':
#     db = MongoDBClient()

#     filter={
#     '_id': ObjectId('<ID AQUI>')
# }
    #Album = Insert_album("EXPLORACAO", r"C:\Users\jmoni\OneDrive\Área de Trabalho\EPI_helmet\petro_links\output\page-exploracao.json")
    #Album.insert()


    # insert_many_images(db, filter)




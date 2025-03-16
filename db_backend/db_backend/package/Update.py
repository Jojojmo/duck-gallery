

from dataclasses import asdict
import logging.config
import pathlib

from bson import ObjectId
from Constraints_rules import has_label_data, image_id_exist, is_catalog_exist
from Insert import Insert_catalog
from Schemas import SchemaCatalog, SchemaImage
from Utils import MongoDBClient

logging.config.fileConfig('logging.ini')
logger_file = logging.getLogger('fileLogger')
logger_terminal = logging.getLogger('terminalLogger')



def update_catalog(client: MongoDBClient, path_json: pathlib.Path, extras: dict = None):
     # Utiliza o nome do arquivo (sem extensão) como _id
    image_id = ObjectId(path_json.stem)
    catalog_id = client.CATALOG_COLLECTION.find_one({'id_image': image_id}, {'_id': 1})['_id']
    filter = {'_id': catalog_id}

    if not is_catalog_exist(client.CATALOG_COLLECTION, catalog_id):
        logger_file.warning(f"Não encontrado _id:{catalog_id} na collection catalog.")
        logger_terminal.warning(f"Não encontrado _id:{catalog_id} na collection catalog.")
        return


    extras = extras or {}
    
    # Tenta obter os dados do LabelMe se o arquivo JSON existir.
    labelme_data = has_label_data(path_json)

    ###MUDAR LER A IMAGEM DO TMP###   
    image_doc = image_id_exist(client.IMAGES_COLLECTION, image_id)
    
    image_data = SchemaImage(**image_doc)
    
    # Cria a instância do catálogo com os dados da imagem e, se existir, os dados do LabelMe.
    catalog_instance = Insert_catalog(
        image_data=image_data,
        labelme_data=labelme_data,
        extras=extras
    )
    
    catalog_schema = SchemaCatalog(**catalog_instance.__dict__)
    catalog_dict = asdict(catalog_schema)
    catalog_dict.pop('_id', None)  # Remove o _id se estiver presente

    result = client.CATALOG_COLLECTION.replace_one(filter, catalog_dict)
    logger_file.info(f"Catálogo atualizado com _id: {catalog_id}, linhas afetadas: {result.modified_count}")
    logger_terminal.info(f"Catálogo atualizado com _id: {catalog_id}, linhas afetadas: {result.modified_count}")
    return result.modified_count

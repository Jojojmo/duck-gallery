import pathlib

import logging.config
from Utils import MongoDBClient
import imagehash
from pymongo.synchronous.collection import Collection


logging.config.fileConfig('logging.ini')
logger_file = logging.getLogger('fileLogger')
logger_terminal = logging.getLogger('terminalLogger')


terminal_hyperlink = lambda link, short_text: f"\033]8;;{link}\033\\{short_text}\033]8;;\033\\"



def album_exist(ALBUM_COLLECTION:Collection, album):
    filter={'album': album}
    project={'_id': 1, 'album': 1}


    result = ALBUM_COLLECTION.find_one(filter=filter,
                                        projection=project)
    if result:
        logger_terminal.warning(f"Album '{album}' já cadastrado: _id={result['_id']}.")
        logger_file.warning(f"Album '{album}' já cadastrado: _id={result['_id']}.")
        return True
    return False


def image_url_exist(IMAGES_COLLECTION:Collection, src):
    filter = {'image_url': src}
    project={'_id': 1}

    result = IMAGES_COLLECTION.find_one(filter=filter,
                                        projection=project)
    if result:
        logger_terminal.warning(f"Url, já existente no banco de dados: _id={result['_id']}. {terminal_hyperlink(src, "Visualize aqui")}")
        logger_file.warning(f"Url, já existente no banco de dados: _id={result['_id']}. Link: {src}")
        return True
    return False
    

def image_id_exist(IMAGES_COLLECTION:Collection, _id):
    image_doc = IMAGES_COLLECTION.find_one({'_id': _id})
    if not image_doc:
        logger_terminal.error(f"Imagem com _id {_id} não encontrada na coleção 'images'.")
        logger_file.error(f"Imagem com _id {_id} não encontrada na coleção 'images'.")
        raise ValueError(f"Imagem com _id {_id} não encontrada na coleção 'images'.")
    return image_doc


def check_hash(IMAGES_COLLECTION:Collection, hash, src, tolerancia=2.5) -> bool:
    project={
    '_id': 1, 
    'hash': 1,
    "image_url": 1
    }
    result = IMAGES_COLLECTION.find(projection=project)
    
    for document in result:
        distancia = imagehash.hex_to_hash(hash) - imagehash.hex_to_hash(document['hash'])
        if distancia < tolerancia:
            link_original = terminal_hyperlink(document['image_url'], 'Imagem Original')
            link_similar= terminal_hyperlink(src, 'Imagem similar')
            logger_terminal.warning(f"Imagem similar encontrada no banco de dados: _id={document['_id']}. "
                                    f"Visualize: {link_original} - {link_similar}.")
            logger_file.warning(f"Imagem similar encontrada no banco de dados: _id={document['_id']}. "
                                f"Url original:{document['image_url']} | Url similar: {src}")
            return False
    return True


def has_label_data(json_path:pathlib.Path):
    from Insert import Get_labelme_data
    if json_path.exists():
        try:
            return Get_labelme_data(json_path)
        except Exception as e:
            logger_terminal.error(f"Erro ao processar o arquivo JSON: {e}")
            logger_file.error(f"Erro ao processar o arquivo JSON: {e}")
            raise ValueError(f"Erro ao processar o arquivo JSON: {e}")
    else:
        logger_file.warning(f"Arquivo JSON não encontrado em {json_path}. Prosseguindo sem labelme_data.")
        logger_terminal.warning(f"Arquivo JSON não encontrado em {json_path}. Prosseguindo sem labelme_data.")



def is_catalog_exist(CATALOG_COLLECTION:Collection, catalog_id):
    if CATALOG_COLLECTION.find_one({'_id': catalog_id}):
        logger_file.warning(f"Catálogo com _id {catalog_id} já existe.")
        logger_terminal.warning(f"Catálogo com _id {catalog_id} já existe.")
        return True



def is_image_in_catalog_exist(CATALOG_COLLECTION:Collection, catalog_id):
    if CATALOG_COLLECTION.find_one({'id_image': catalog_id}):
        logger_file.warning(f"Catálogo já possui a imagem de _id {catalog_id}.")
        logger_terminal.warning(f"atálogo já possui a imagem de _id {catalog_id}.")
        return True





import base64
from pathlib import Path

from Schemas import SchemaImage

import logging.config

logging.config.fileConfig('logging.ini')
logger_file = logging.getLogger('fileLogger')


def save_image(document_image: SchemaImage, folder:Path):
    # Se a imagem for uma string, decodifica do base64;
    # caso contrário, assume que já é binária
    if isinstance(document_image.imagem, str):
        imagem_data = base64.b64decode(document_image.imagem)
    else:
        imagem_data = document_image.imagem

    file_path = folder / f"{str(document_image._id)}.jpg"

    with open(file_path, "wb") as file:
        file.write(imagem_data)
    logger_file.info(f"Imagem: {str(document_image._id)} baixada com sucesso!")


def save_many_imges(id_images:list, folder:Path):
    for image in id_images:
        document = SchemaImage(**image)
        save_image(document, folder)


if __name__ == '__main__':
    from pathlib import Path
    from Utils import MongoDBClient
    from bson import ObjectId


    db = MongoDBClient()
    
    # Exemplo save único
    filter = {
        '_id': ObjectId('<ID EXEMPLO AQUI>')
    }
    
    result = db.IMAGES_COLLECTION.find_one(filter=filter)

    document = SchemaImage(**result) # ALERTA NO NONETYPE, SE O ID NÃO EXISTIR, DA ERRO
    dir = r".\tmp"
    PATH_DIR = Path(dir)


    PATH_DIR.mkdir(parents=True, exist_ok=True)

    save_image(document, dir)

    images = [
    "<ID EXEMPLO AQUI>",
    "<ID EXEMPLO AQUI>"
    ]
    
    save_many_imges(images, PATH_DIR)





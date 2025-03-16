

from enum import Enum
from typer import Context, Exit, Typer, Argument, Option, BadParameter


from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table


import sys
from collections import Counter
from pathlib import Path
import shutil


# Aqui, BASE_DIR já é a pasta "code"
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from package.Utils import MongoDBClient
from package.Save_image import save_many_imges
from package.Insert import insert_catalog
from package.Update import update_catalog

from cli.Support import saves_labelme

app = Typer()
console = Console()
__version__ = '0.0.1'

#Constanst
db = MongoDBClient('mongodb://localhost:8081/')
TMP_NAME = r'temp' #r'..\do_label\temp'
TMP_DIR = Path(TMP_NAME)

def version(arg):
    if arg:
        print(__version__)
        raise Exit(code=0)


@app.callback(invoke_without_command=True)
def callcaback(
    ctx: Context,
    version: bool = Option(
        False,
        '--version', '-v', '--versao',
        callback=version,
        is_eager=True,
        is_flag=True,
        case_sensitive=False
    )
):
    if ctx.invoked_subcommand:
        return
    print(Panel.fit("Use os seguintes comandos [purple b]next[/], [purple b]post[/], [purple b]recent[/] ou [purple b]describe[/]"))


class AlbumTypes(Enum):
    HISTORICA  = "HISTORICA" 
    EXPLORACAO = "EXPLORACAO"
    REFINO     = "REFINO"
    GAS        = "GAS" 
    ELETRICA   = "ELETRICA" 
    TRANSPORTE = "TRANSPORTE" 
    RENOVAVEL  = "RENOVAVEL" 
    PATROCINIO = "PATROCINIO"
    NONE       = "NONE"



def has_album(album_key):
    result = db.ALBUM_COLLECTION.find_one({"album": album_key}, {"_id": 1})
    
    if not result:
        print(f"[red b u]Album indisponível ou não encontrado:[/] {album_key}")
        raise Exit(code=1)
    return result["_id"]


def count_labels(marks_list):
    counter = Counter()

    for boxes in marks_list:
        if not boxes:  
            boxes = [{}]
        counter.update(obj.get('label', 'background') for obj in boxes)
    

    return counter

@app.command("next")
def next(
    album_key: AlbumTypes = Argument(help="Nome do álbum selecionado."),
    limit: int = Option(20, help="Quantidade de imagens a serem baixadas")
):
    """
    Busca e baixa o próximo conjunto de imagens que ainda não estão catalogadas para o álbum informado.
    """
    
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    album_id = has_album(album_key.value)

    catalog_items = db.CATALOG_COLLECTION.find({"id_album": album_id}, {"id_image": 1}).to_list()
    catalog_ids = list(map(lambda doc: doc["id_image"], catalog_items))

    results = db.IMAGES_COLLECTION.find({"_id": {"$nin": catalog_ids}}).limit(limit).to_list()    

    save_many_imges(results, TMP_DIR)



@app.command('post')
def post():
    """
    Insere as imagens catalogadas no banco de dados e exlui a pasta temporária.
    """
    list_jpg = [file for file in TMP_DIR.iterdir() if file.suffix.lower() == ".jpg"]
    for image in list_jpg:
        labeled = image.with_suffix(".json")
        try:
            insert_catalog(client=db, path_json=labeled)
        except Exception as e:
            print(f"[red b u]Erro ao inserir em catalog.[/] Error: {e}")
            raise Exit(code=1)            

    shutil.rmtree(TMP_NAME)


@app.command('update')
def update():
    """
    Atuliza as imagens catalogadas no banco de dados e exlui a pasta temporária.
    """    
    list_jpg = [file for file in TMP_DIR.iterdir() if file.suffix.lower() == ".jpg"]
    for image in list_jpg:
        labeled = image.with_suffix(".json")
        try:
            update_catalog(client=db, path_json=labeled)
        except Exception as e:
            print(f"[red b u]Erro ao inserir em catalog.[/] Error: {e}")
            raise Exit(code=1)            

    shutil.rmtree(TMP_NAME)


@app.command('recent')
def recent(
    limit: int = Option(20, help="Quantidade de imagens a serem baixadas")
):
    """
    Baixa as imagens catalogadas mais recentes
    """

    TMP_DIR.mkdir(parents=True, exist_ok=True)

    project={'marks': 0, 'created_at':0,'extras': 0} #Quando atualizar os extras, a lógica tem que ser alterada
    sort=list({'created_at': -1}.items())

    latest_docs = db.CATALOG_COLLECTION.find(projection=project, sort=sort).limit(limit).to_list()

    files_labelme = {doc['id_image']: doc['labelme_file'] for doc in latest_docs}
    for doc in latest_docs:
        doc.pop('labelme_file')
        doc['_id'] = doc.pop('id_image')


    save_many_imges(latest_docs, TMP_DIR)
    saves_labelme(files_labelme, TMP_DIR)


@app.command('describe')
def describe(
    album_key: AlbumTypes = Option("NONE", help="Nome do álbum selecionado."), 
    coverage: bool = Option(False),
    labels: bool = Option(False)
):
    """
    Descreve informações consolidadas das imagens catalogadas.
    """
    filter = {}
    if album_key != AlbumTypes.NONE:
        album_id = has_album(album_key.value)
        filter['id_album'] = album_id

    count_catalog = db.CATALOG_COLLECTION.count_documents(filter)
    count_images = db.IMAGES_COLLECTION.count_documents(filter)

    # Tabela: Document Registers
    table_registers = Table(title="Document Registers", width=25)
    table_registers.add_column("Collection", style="cyan")
    table_registers.add_column("Total", justify="right")
    table_registers.add_row("count_catalog", str(count_catalog))
    table_registers.add_row("count_images", str(count_images))
    console.print(table_registers)

    if coverage:
        coverage_percentage = round((count_catalog / count_images) * 100, 2) if count_images else 0
        panel_coverage = Panel(f"[green b]{coverage_percentage}%[/]", title="Coverage", title_align="left",width=25)
        console.print(panel_coverage)

    if labels:
        marks_obj = db.CATALOG_COLLECTION.find(filter=filter, projection={'marks':1, '_id':0})
        marks_list = list(map(lambda doc: doc['marks'], marks_obj))
        counter_labels = count_labels(marks_list)


        labels_table = Table(title="Labels", width=25)
        labels_table.add_column("Label", style="magenta")
        labels_table.add_column("Total", justify="right")
        for label, counter in counter_labels.items():
            labels_table.add_row(label, str(counter))
        console.print(labels_table)


app()




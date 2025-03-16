Passo 1, criar o ambiente virtual:

```
python -m venv .env
```

ative ele

```
.env/Scripts/activate
```

instale 

```
pip install -r requirements.txt
```

## Para Catalogar

Entre no ambiente:
```
.env/Scripts/activate
```

rode o comando:
```
labelme ..\db_backend\temp\ --output ..\db_backend\temp\ --nodata
```
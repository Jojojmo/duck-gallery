import json

def saves_labelme(files_labelme, TMP_DIR):
    for id, content in files_labelme.items():
        path_id = TMP_DIR / f"{str(id)}.json"
        if content:
            with open(path_id, 'w') as file:
                json.dump(content, file, indent=2)
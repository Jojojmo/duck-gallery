
from pymongo import MongoClient



class MongoDBClient:
    def __init__(self, host='mongodb://localhost:27017/', db_name='epp_helmet'):
        self.client = MongoClient(host)
        self.db = self.client[db_name]
        self.session = self.client.start_session()
        
        # Define globalmente as coleções
        self.ALBUM_COLLECTION = self.db['album']
        self.IMAGES_COLLECTION = self.db['images']
        self.CATALOG_COLLECTION = self.db['catalog']
    
    def close(self):
        # Encerra a sessão e o client
        self.session.end_session()
        self.client.close()
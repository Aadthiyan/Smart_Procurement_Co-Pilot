import os
import json
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

load_dotenv('src/config/cloud.env')

class DatabaseManager:
    def __init__(self):
        self.use_cloud = False
        self.client = None
        self.local_db_path = 'local_db.json'
        
        # Try to connect to Cloudant
        if os.getenv('CLOUDANT_APIKEY') and os.getenv('CLOUDANT_URL'):
            try:
                authenticator = IAMAuthenticator(os.getenv('CLOUDANT_APIKEY'))
                self.client = CloudantV1(authenticator=authenticator)
                self.client.set_service_url(os.getenv('CLOUDANT_URL'))
                self.use_cloud = True
                print("Connected to IBM Cloudant.")
                
                # Check if DB exists, create if not
                try:
                    self.client.get_database_information(db='procurement_db').get_result()
                except Exception:
                    print("Database 'procurement_db' not found. Creating it...")
                    self.client.put_database(db='procurement_db').get_result()
                    print("Database 'procurement_db' created.")
                    
            except Exception as e:
                print(f"Failed to connect to Cloudant: {e}. Falling back to local storage.")
                self.use_cloud = False
        else:
            print("No Cloudant credentials found. Using local storage.")

        if not self.use_cloud:
            self._init_local_db()

    def _init_local_db(self):
        if not os.path.exists(self.local_db_path):
            with open(self.local_db_path, 'w') as f:
                json.dump({"vendors": [], "requisitions": []}, f)

    def _read_local_db(self):
        with open(self.local_db_path, 'r') as f:
            return json.load(f)

    def _write_local_db(self, data):
        with open(self.local_db_path, 'w') as f:
            json.dump(data, f, indent=2)

    def save_vendor(self, vendor_data):
        if self.use_cloud:
            doc = {
                "type": "vendor",
                **vendor_data
            }
            response = self.client.post_document(db='procurement_db', document=doc).get_result()
            return response['id']
        else:
            db = self._read_local_db()
            vendor_data['id'] = f"ven_{len(db['vendors']) + 1}"
            db['vendors'].append(vendor_data)
            self._write_local_db(db)
            return vendor_data['id']

    def get_vendor(self, vendor_id):
        if self.use_cloud:
            # Implementation for Cloudant fetch would go here
            pass
        else:
            db = self._read_local_db()
            for v in db['vendors']:
                if v.get('id') == vendor_id or v.get('tax_id') == vendor_id:
                    return v
            return None

    def save_requisition(self, req_data):
        if self.use_cloud:
            doc = {
                "type": "requisition",
                **req_data
            }
            response = self.client.post_document(db='procurement_db', document=doc).get_result()
            return response['id']
        else:
            db = self._read_local_db()
            req_data['id'] = f"req_{len(db['requisitions']) + 1}"
            db['requisitions'].append(req_data)
            self._write_local_db(db)
            return req_data['id']

# Singleton instance
db_manager = DatabaseManager()

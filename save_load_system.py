# save_load_system.py - PDS-X BASIC v14u Save/Load System
# Version: 1.0.0
# Date: May 15, 2025
# Author: Mete Dinler

from auto_importer import importer
from pdsx_exception import PdsXException

# Import libraries dynamically
importer.import_libraries("save_load_system")

# Assign imported modules
json = importer.get_module("json")
base64 = importer.get_module("base64")
gzip = importer.get_module("gzip")
zlib = importer.get_module("zlib")
pickle = importer.get_module("pickle")

format_registry = {
    "json": {
        "encode": lambda data: json.dumps(data).encode("utf-8"),
        "decode": lambda data: json.loads(data.decode("utf-8"))
    },
    "pickle": {
        "encode": pickle.dumps,
        "decode": pickle.loads
    }
}

supported_encodings = {
    "base64": {
        "encode": base64.b64encode,
        "decode": base64.b64decode
    }
}

compression_methods = {
    "gzip": gzip.compress,
    "zlib": zlib.compress
}

decompression_methods = {
    "gzip": gzip.decompress,
    "zlib": zlib.decompress
}

class SaveLoadSystem:
    def __init__(self):
        self.format = "pickle"
        self.encoding = "base64"
        self.compression = "gzip"
        
    def save(self, data, file_path: str):
        try:
            encoded_data = format_registry[self.format]["encode"](data)
            if self.compression:
                encoded_data = compression_methods[self.compression](encoded_data)
            if self.encoding:
                encoded_data = supported_encodings[self.encoding]["encode"](encoded_data)
            with open(file_path, "wb") as f:
                f.write(encoded_data)
        except Exception as e:
            raise PdsXException(f"Veri kaydetme hatası: {str(e)}")
    
    def load(self, file_path: str):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            if self.encoding:
                data = supported_encodings[self.encoding]["decode"](data)
            if self.compression:
                data = decompression_methods[self.compression](data)
            return format_registry[self.format]["decode"](data)
        except Exception as e:
            raise PdsXException(f"Veri yükleme hatası: {str(e)}")

if __name__ == "__main__":
    print("save_load_system.py cannot be run standalone. Use with pdsXbasic.")
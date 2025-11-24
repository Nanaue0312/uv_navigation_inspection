import json
from typing import Dict, Any, Union, List

def load_data(file_content: str) -> Dict[str, Any]:
    """
    Load analysis data from file content (string).
    Handles standard JSON and concatenated JSON objects.
    """
    try:
        data = json.loads(file_content)
        return data
    except json.JSONDecodeError:
        # Try handling multiple objects if simple load fails
        data_objects = []
        decoder = json.JSONDecoder()
        pos = 0
        while pos < len(file_content):
            file_content = file_content.strip()
            if file_content.startswith(','):
                file_content = file_content[1:].strip()
            if not file_content:
                break
            try:
                obj, idx = decoder.raw_decode(file_content)
                data_objects.append(obj)
                file_content = file_content[idx:].strip()
                pos = 0 
            except json.JSONDecodeError:
                break
        
        if len(data_objects) == 1:
            if isinstance(data_objects[0], list):
                return {'frames': data_objects[0]}
            elif isinstance(data_objects[0], dict) and 'frames' in data_objects[0]:
                return data_objects[0]
            else:
                return {'frames': data_objects}
        else:
            return {'frames': data_objects}

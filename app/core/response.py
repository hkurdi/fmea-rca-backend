import json
from datetime import datetime
from enum import Enum
from fastapi.responses import JSONResponse


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


def success_response(data=None, message: str = "Success", status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content=json.loads(json.dumps(
            {"success": True, "data": data, "message": message},
            cls=CustomEncoder,
        )),
    )


def error_response(message: str = "Error", status_code: int = 400, data=None):
    return JSONResponse(
        status_code=status_code,
        content=json.loads(json.dumps(
            {"success": False, "data": data, "message": message},
            cls=CustomEncoder,
        )),
    )
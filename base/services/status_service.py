from datetime import datetime

from rest_framework.response import Response


class StatusService:
    def __init__(self):
        pass

    def _build_response(self, success: bool, code: int, data: object, message: str) -> Response:
        return Response({
            "success": success,
            "data": data,
            "message": message or ("Success" if success else "Failure"),
            "code": code,
            'timestamp': int(datetime.now().timestamp())
        }, status=code)

    def status200(self, data: object, message: str = "Success") -> Response:
        return self._build_response(True, 200, data, message)

    def status201(self, data: object, message: str = "Success") -> Response:
        return self._build_response(True, 201, data, message)

    def status204(self, data: object = None, message: str = "Success") -> Response:
        return self._build_response(True, 204, data, message)

    def status400(self, data: object, message: str = "Failure") -> Response:
        return self._build_response(False, 400, data, message)

    def status404(self, data: object, message: str = "Failure") -> Response:
        return self._build_response(False, 404, data, message)

    def status500(self, data: object, message: str = "Failure") -> Response:
        return self._build_response(False, 500, data, message)

    def status405(self, data: object, message: str = "Not Allow") -> Response:
        return self._build_response(False, 405, data, message)
    
    def status401(self, data: object, message: str = "Unauthorized") -> Response:
        return self._build_response(False, 401, data, message)

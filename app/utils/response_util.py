from fastapi.responses import JSONResponse
from fastapi import status


def res_error(message: str):
  return JSONResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    content={
      'message': message
    }
  )
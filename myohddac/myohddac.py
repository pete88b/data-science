import time
import base64
import pathlib
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

output_dir = 'images'
decode =  base64.urlsafe_b64decode

pathlib.Path(output_dir).mkdir(exist_ok=True)

def homepage(request):
    return FileResponse('static/index.html')

async def save_img(request):
    request_body = await request.json()
    f_name = '%s/%s-%s.png' % (output_dir, request_body['number'], time.time())
    with open(f_name, 'wb') as f:
        f.write(decode(request_body['img'][22:]))
    return JSONResponse({'message':'saved as ' + f_name})
    
routes = [
    Route('/', homepage),
    Route('/img/save', save_img, methods=['POST']),
    Mount('/', StaticFiles(directory='static'))
]

app = Starlette(routes=routes)
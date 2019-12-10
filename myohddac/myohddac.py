import time
import json
import pathlib
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

output_dir = 'numbers'

pathlib.Path(output_dir).mkdir(exist_ok=True)

def homepage(request):
    return FileResponse('static/index.html')

async def save_img(request):
    request_body = await request.json()
    f_name = '%s/%s-%s.json' % (output_dir, request_body['number'], time.time())
    with open(f_name, 'w') as f:
        json.dump(request_body['img'], f)
    return JSONResponse({'message':'saved as ' + f_name})
    
routes = [
    Route('/', homepage),
    Route('/img/save', save_img, methods=['POST']),
    Mount('/', StaticFiles(directory='static'))
]

app = Starlette(routes=routes)
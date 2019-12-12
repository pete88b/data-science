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

try:
    from fastai.vision import open_image
    from fastai.basic_train import load_learner
    import io
    learn_export_file_name = 'stage-1-export.pkl'
    learn = load_learner('notebooks', learn_export_file_name)
    print('INFO: running with predictions')
    
except ModuleNotFoundError as ex:
    print('INFO: running without predictions as fastai not found')

except FileNotFoundError as ex:
    print('INFO: running without predictions as %s not found' % learn_export_file_name)

def homepage(request):
    return FileResponse('static/index.html')

async def save_img(request):
    request_body = await request.json()
    number = request_body['number']
    prediction_category = 'o'
    try:
        image_bytes = io.BytesIO(base64.urlsafe_b64decode(request_body['img'][22:]))
        image = open_image(image_bytes) 
        predictions = learn.predict(image)
        prediction = predictions[2].max(-1)[1].item()
        probablity = predictions[2][prediction].item()
        prediction_category = 'y' if prediction == number else 'n'
        # might also be good to flag correct predictions with low probability
        f_name = '%s/%s-%s-%s.png' % (output_dir, number, prediction_category, time.time())
        image.save(f_name)

    except:
        prediction = None
        probablity = None
        f_name = '%s/%s-%s.png' % (output_dir, number, time.time())
        with open(f_name, 'wb') as f:
            f.write(decode(request_body['img'][22:]))

    return JSONResponse({
        'savedAs': f_name,
        'prediction': prediction,
        'probablity': probablity})
    
routes = [
    Route('/', homepage),
    Route('/img/save', save_img, methods=['POST']),
    Mount('/', StaticFiles(directory='static'))
]

app = Starlette(routes=routes)
import time
import base64
import pathlib
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

output_dir = 'images'
pathlib.Path(output_dir).mkdir(exist_ok=True)
decode =  base64.urlsafe_b64decode

try:
    from fastai.vision import open_image
    import io
except ModuleNotFoundError as ex:
    print('INFO: running without predictions as fastai not found')

def _load_learner(export_file_name, label):
    try:
        from fastai.basic_train import load_learner
        learn = load_learner('notebooks', export_file_name)
        print(f'INFO: running with {label}')
        return learn
    except ModuleNotFoundError as ex:
        print(f'INFO: running without {label} as fastai not found')
    except FileNotFoundError as ex:
        print(f'INFO: running without {label} as {export_file_name} not found')

learn = _load_learner('mnist-learn-export.pkl', 'predictions')
mnist_or_not_learn = _load_learner('mnist-or-not-learn-export.pkl', 'mnist or not')
mnist_or_not_thresh = None if mnist_or_not_learn is None else mnist_or_not_learn.model.opt_thresh

def homepage(request):
    return FileResponse('static/index.html')

async def save_img(request):
    request_body = await request.json()
    number = request_body['number']
    prediction_category = 'o'
    try:
        def r(t): return round(t.item(), 3)
        image_bytes = io.BytesIO(base64.urlsafe_b64decode(request_body['img'][22:]))
        image = open_image(image_bytes)
        mnist_or_not_score = r(mnist_or_not_learn.predict(image)[1])
        predictions = learn.predict(image)
        prediction = predictions[2].max(-1)[1].item()
        score = r(predictions[2][prediction])
        prediction_category = 'y' if prediction == number else 'n'
        # might also be good to flag correct predictions with low probability
        f_name = '%s/%s-%s-%s.png' % (output_dir, number, prediction_category, time.time())
        image.save(f_name)
    except:
        mnist_or_not_score = None
        prediction = None
        score = None
        f_name = '%s/%s-%s.png' % (output_dir, number, time.time())
        with open(f_name, 'wb') as f:
            f.write(decode(request_body['img'][22:]))

    return JSONResponse({
        'savedAs': f_name,
        'prediction': prediction,
        'score': score,
        'mnistOrNotScore': mnist_or_not_score,
        'mnistOrNotThresh': mnist_or_not_thresh})
    
routes = [
    Route('/', homepage),
    Route('/img/save', save_img, methods=['POST']),
    Mount('/', StaticFiles(directory='static'))
]

app = Starlette(routes=routes)
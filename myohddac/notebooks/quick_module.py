# Created by NbdevQuick
from fastai.vision import *
import shutil, PIL
from pathlib import Path
#NbdevQuick:start(mnist_path)
mnist_path=untar_data(URLs.MNIST)
#NbdevQuick:end(mnist_path)
#NbdevQuick:start(mnist_data)
def mnist_data(stats=None,flip_t_and_v=False):
    tfms = get_transforms(do_flip=False)
    t_and_v = ['training','testing']
    if flip_t_and_v: t_and_v.reverse()
    db = ImageDataBunch.from_folder(
        mnist_path, train=t_and_v[0], valid=t_and_v[1], ds_tfms=tfms, size=28, bs=128)
    db.normalize() if stats is None else db.normalize(stats)
    return db
#NbdevQuick:end(mnist_data)
#NbdevQuick:start(conv_block)
def conv_block(in_channels, out_channels, padding=1):
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, 3, padding=padding),
        nn.ReLU(),
        nn.MaxPool2d((2,2)))

def fc_block(in_features, out_features):
    return nn.Sequential(
        nn.Linear(in_features, out_features),
        nn.ReLU())

def new_model(c_out=10):
    return nn.Sequential(
        conv_block(3, 32, padding=2),
        conv_block(32, 32),
        conv_block(32, 32),
        nn.Flatten(),
        fc_block(288, 84),
        nn.Linear(84, c_out))
#NbdevQuick:end(conv_block)
#NbdevQuick:start(save)
def save(name,learn,data):
    learn.save(f'{name}-learn')
    # export the model for inference
    learn_export_file_name = f'{name}-learn-export.pkl'
    learn.export(learn_export_file_name)
    # Export the minimal state of the data bunch for inference 
    data_export_file_name = f'{name}-data-export.pkl'
    data.export(data_export_file_name)
    here = Path('.')
    # copy the export files from fastai default to here
    for file_name in [learn_export_file_name, data_export_file_name]:
        shutil.copyfile(learn.path/file_name, here/file_name)
    return learn_export_file_name,data_export_file_name
#NbdevQuick:end(save)
#NbdevQuick:start(can_call_with_n_positional_args)
def can_call_with_n_positional_args(f, n):
    "return true if f can be called with n positional arguments, false otherwise"
    def _len(l): return 0 if l is None else len(l)
    fas = inspect.getfullargspec(f)
    def _min(): return _len(fas.args) - _len(fas.defaults)
    def _max(): return 99999 if fas.varargs else len(fas.args)
    if inspect.ismethod(f): n += 1 # add one for self
    return n >= _min() and n <= _max()
#NbdevQuick:end(can_call_with_n_positional_args)
#NbdevQuick:start(_create_not_digits)
def _create_not_digits(input_path, output_path, kind, digit, converters):
    print('converting', kind, digit)
    (output_path/f'{kind}/not{digit}').mkdir(parents=True, exist_ok=True)
    for i, f in enumerate((input_path/f'{kind}/{digit}').iterdir()):
        converter=converters[i % len(converters)]
        output_file=output_path/f'{kind}/not{digit}/{f.name}'
        args=[PIL.Image.open(f)]
        if can_call_with_n_positional_args(converter,4): args=args+[input_path,kind,digit]
        converter(*args).save(output_file)
        
def create_not_digits(path, digit, converters, ds_name='mnist_or_not'):
    output_path = path.parent/ds_name
    _create_not_digits(path, output_path, 'training', digit, converters)
    _create_not_digits(path, output_path, 'testing', digit, converters)
#NbdevQuick:end(_create_not_digits)
#NbdevQuick:start(cp_mnist)
def cp_mnist(kind, ds_name='mnist_or_not'):
    p = mnist_path/kind
    o = output_path = mnist_path.parent/f'{ds_name}/{kind}'
    print(f'copying from {p} to {o}')
    get_ipython().system('cp -r -u $p/. $o')
#NbdevQuick:end(cp_mnist)
#NbdevQuick:start(mnist_or_not_data)
def mnist_or_not_data(path, stats=None):
    tfms=get_transforms(do_flip=False)
    return (ImageList.from_folder(path)
        .split_by_folder(train='training', valid='testing')
        .label_from_func(lambda x: 0. if 'not' in x.parts[-2] else 1.)
        .transform(tfms, size=28)
        .databunch(bs=256)
        .normalize(imagenet_stats))
#NbdevQuick:end(mnist_or_not_data)
#NbdevQuick:start(get_y_preds_and_actuals)
def get_y_preds_and_actuals(learn):
    y_preds,y_actuals=[],[]
    with torch.no_grad():
        for i, (xb, yb) in enumerate(learn.data.valid_dl):
            y_pred = learn.model(xb)
            y_pred = torch.flatten(y_pred)
            y_preds.append(y_pred)
            y_actuals.append(yb)
    return torch.cat(y_preds),torch.cat(y_actuals)
#NbdevQuick:end(get_y_preds_and_actuals)
#NbdevQuick:start(search_optimal_thresh)
def search_optimal_thresh(start,step,y_preds,y_actuals,result=[0],depth=0,max_depth=3):
    for i in range(11):
        thresh=(i*step)+start
        acc=accuracy_thresh(y_preds,y_actuals,thresh,False).item()
        if acc>result[0]: result=[acc,thresh]
    if depth<max_depth:
        return search_optimal_thresh(result[1]-step, step/5, y_preds, y_actuals, result, depth+1)
    return result
#NbdevQuick:end(search_optimal_thresh)
#NbdevQuick:start(regressor_acc_vs_classes)
def regressor_acc_vs_classes(learn,ylim):
    """for each class of digit, see how accurate the model is"""
    # TODO: do somthing for not digits
    d,opt_thresh=[],learn.model.opt_thresh
    learn.data.batch_size=2048
    for cls in range(10):
        image_list=ImageList.from_folder(learn.path/f'testing/{cls}')
        learn.data.add_test(image_list)
        xb,_=next(iter(learn.data.test_dl))
        output=learn.model(xb).flatten()
        d.append([cls]+[(output>t).sum().item()/len(xb) for t in [opt_thresh-.1, opt_thresh, opt_thresh+.1]])
    df = pd.DataFrame(d, columns=['Class', '-0.1', opt_thresh, '+0.1'])
    df.plot.bar(x='Class', ylim=ylim); plt.legend(ncol=3); plt.xlabel('Classes');
#NbdevQuick:end(regressor_acc_vs_classes)

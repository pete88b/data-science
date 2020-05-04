# Created by NbdevQuick
from fastai.vision import *
import shutil
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
#NbdevQuick:start(mnist_data)
def mnist_data(stats=None,flip_t_and_v=False):
    path = untar_data(URLs.MNIST); path
    tfms = get_transforms(do_flip=False)
    t_and_v = ['training','testing']
    if flip_t_and_v: t_and_v.reverse()
    db = ImageDataBunch.from_folder(
        path, train=t_and_v[0], valid=t_and_v[1], ds_tfms=tfms, size=28, bs=128)
    db.normalize() if stats is None else db.normalize(stats)
    return db
#NbdevQuick:end(mnist_data)

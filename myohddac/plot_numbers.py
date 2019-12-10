import os
import json
import numpy as np
import matplotlib.pyplot as plt

style = {'cmap': 'gray', 'title_color': 'white'} # black background
# style = {'cmap': 'binary', 'title_color': 'black'} # white background

fig = plt.figure(figsize=(6, 6))
columns = 4
rows = 5

try:
    dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'numbers'))
    print('reading files from', dir)
    if list(os.listdir(dir)) == []:
        raise Exception('%s is empty' % dir)
except Exception as ex:
    print('Please run the web app and create some files.', ex)
    exit()

file_name_map = {}
# group files by the number they represent
for file_name in os.listdir(dir):
    key = file_name[0]
    if key in file_name_map:
        file_name_map[key].append(file_name)
    else:
        file_name_map[key] = [file_name]

file_names = []
# pick 2 files to show, from each group, at random
for value in file_name_map.values():
    np.random.shuffle(value)
    file_names.extend(value[:2])

file_names.sort(key=lambda f_name: f_name[0])

for i, file_name in enumerate(file_names):
    # read the "image" file and convert to 28*28 array
    with open(os.path.join(dir, file_name)) as f:
        data = json.load(f)
    data = np.reshape(data, (-1, 28))
    # add the image to the plot
    fig.add_subplot(rows, columns, i+1)
    plt.imshow(data, cmap=style['cmap'])
    plt.title(file_name[0], x=0.1, y=0.7, color=style['title_color'])
    plt.xticks([])
    plt.yticks([])
    
plt.show()
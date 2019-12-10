myohddac is;
- a web app that makes it easy to "make your own hand drawn digits and characters"
- some tools to help working the data created by the web app.

In README.txt {myohddac_home} means the location of this project in your file system.
    e.g. /Users/Someone/Projects/myohddac or C:\Users\Someone\Projects\myohddac

To run the web app locally;
cd {myohddac_home}
uvicorn myohddac:app --reload

Files will be saved to: {myohddac_home}/numbers
    see myohddac.py if you need to change this

Please note: No attempt has been made to make the web app secure

To plot a selection of numbers;
cd {myohddac_home}
python plot_numbers.py
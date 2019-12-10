app = {};
app.namesOfNumbers = [
    'zero', 'one', 'two', 'three', 'four',
    'five', 'six', 'seven', 'eight', 'nine'];
app.canvases = [];
app.grabCanvas = function (id, lineWidth, scale) {
    canvas = document.getElementById(id);
    canvas._lineWidth = lineWidth;
    canvas._scale = scale;
    app.canvases.push(canvas);
    app[id] = canvas;
};
app.grabCanvas('inputCanvas', 5, 1); // we draw on this canvas
app.grabCanvas('previewCanvas', 2, 0.25); // and write to this canvas which is 1/4 size

app.inputCanvas.addEventListener('mousedown', e => {
    app.setCursorPositions(e);
    app.isDrawing = true;
    app.inputCanvas.style.cursor = 'pointer';
});
app.inputCanvas.addEventListener('mouseout', e => {
    app.stopDrawing();
});
app.inputCanvas.addEventListener('mousemove', e => {
    app.drawLine(e)
});
app.inputCanvas.addEventListener('mouseup', e => {
    app.drawLine(e);
    app.stopDrawing();
});
/**
 * Translate cursor positions from the event, to poitions on canvases.
 */
app.setCursorPositions = function (e) {
    rect = app.inputCanvas.getBoundingClientRect();
    app.canvases.forEach(function(canvas, i) {
        canvas._clientX = (e.clientX - rect.left) * canvas._scale;
        canvas._clientY = (e.clientY - rect.top) * canvas._scale;
    });
};
app.stopDrawing = function () {
    app.isDrawing = false;
    app.inputCanvas.style.cursor = 'auto';
    app.setUserFeedbackMessage(app.hasDrawn()
            ? 'Press S to save or C start again' : '');
};
app.drawLine = function (e) {
    if (app.isDrawing !== true) {
        return;
    }
    app.canvases.forEach(function(canvas, i) {
        context = canvas.getContext('2d');
        context.beginPath();
        context.strokeStyle = 'black';
        context.lineWidth = canvas._lineWidth;
        context.moveTo(canvas._clientX, canvas._clientY);
    });
    
    app.setCursorPositions(e);
    
    app.canvases.forEach(function(canvas, i) {
        context = canvas.getContext('2d');
        context.lineTo(canvas._clientX, canvas._clientY);
        context.stroke();
        context.closePath();
    });
};
/**
 * Return a 1d array containing grayscale pixel values of a 28*28 image.
 */
app.getCanvasData = function () {
    result = []
    context = app.previewCanvas.getContext('2d');
    context.getImageData(0, 0, 28, 28).data.forEach(function (pixelValue, i) {
        if (i % 4 === 3) {
            result.push(pixelValue);
        }
    });
    return result;
}
/**
 * Return true if we have anything drawn, false otherwise.
 */
app.hasDrawn = function () {
    return Math.max(...app.getCanvasData()) > 0;
};
app.pickNumberAtRandom = function () {
    app.currentNumber = Math.floor(Math.random() * 10);
    document.getElementById('currentNumber').textContent 
            = app.namesOfNumbers[app.currentNumber];
};
app.setUserFeedbackMessage = function (message, imgDataUrl) {
    document.getElementById('userFeedbackMessage').textContent = message;
    document.getElementById('previewImg').src 
            = (imgDataUrl) ? imgDataUrl : '';
};
app.clearCanvas = function () {
    app.inputCanvas.getContext('2d').clearRect(0, 0, 112, 112);
    app.previewCanvas.getContext('2d').clearRect(0, 0, 28, 28);
    app.setUserFeedbackMessage('');
};
/**
 * Post the user entered data to the server.
 */
app.save = function () {
    if (!app.hasDrawn()) {
        return;
    }
    imgDataUrl = app.previewCanvas.toDataURL('image/png');
    xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState === 4) {
            // check HTTP status
            app.reset();
            app.setUserFeedbackMessage(
                JSON.parse(xhr.responseText).message,
                imgDataUrl);
        }
    };
    xhr.open('POST', '/img/save', true);
    xhr.send(JSON.stringify({
        number: app.currentNumber,
        img: app.getCanvasData()
    }));
};
window.addEventListener('keydown', function(e) {
    if (['Backspace', 'Delete', 'c', 'C'].includes(e.key)) {
        e.preventDefault(); // prevent back-navigation on Backspace
        app.clearCanvas();
    } else if (['Enter', 's', 'S'].includes(e.key)) {
        app.save();
    }
});
app.reset = function () {
    app.clearCanvas();
    app.pickNumberAtRandom();
};
app.reset();
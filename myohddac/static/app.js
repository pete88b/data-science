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
app.grabCanvas('previewCanvas', 2, 0.25); // and also write to this canvas which is 1/4 size

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
    app.setUserFeedbackMessage({
        saveOrCancelMessage: app.hasDrawn
    });
};
app.drawLine = function (e) {
    if (app.isDrawing !== true) {
        return;
    }
    app.canvases.forEach(function(canvas, i) {
        context = canvas.getContext('2d', {alpha: false});
        context.beginPath();
        context.strokeStyle = 'white';
        context.lineWidth = canvas._lineWidth;
        context.moveTo(canvas._clientX, canvas._clientY);
    });
    
    app.setCursorPositions(e);
    
    app.canvases.forEach(function(canvas, i) {
        context = canvas.getContext('2d', {alpha: false});
        context.lineTo(canvas._clientX, canvas._clientY);
        context.stroke();
        context.closePath();
    });

    app.hasDrawn = true;
};
app.pickNumberAtRandom = function () {
    app.currentNumber = Math.floor(Math.random() * 10);
    document.getElementById('currentNumber').textContent 
            = app.namesOfNumbers[app.currentNumber];
};
app.setUserFeedbackMessage = function (options) {
    options = options || {} // avoid null references to options
    document.getElementById('saveOrCancelMessage').style.display 
            = options.saveOrCancelMessage ? 'inline' : 'none';
    document.getElementById('previewImg').src 
            = (options.imgDataUrl) ? options.imgDataUrl : '';
    message = ''
    if (options.probablity) {
        options.probablity = Math.round(options.probablity * 1000) / 1000;
        if (options.target === options.prediction) {
            message = 'correctly predicted with a probability of ' + options.probablity;
        } else {
            message = 'incorrectly predicted to be ' + options.prediction
                    + ' with a probability of ' + options.probablity;
        }
    } else if (options.savedAs) {
        message = 'saved as ' + options.savedAs;
    }
    document.getElementById('userFeedbackMessage').textContent = message;
    
};
app.clearCanvas = function () {
    app.inputCanvas.getContext('2d', {alpha: false}).clearRect(0, 0, 112, 112);
    app.previewCanvas.getContext('2d', {alpha: false}).clearRect(0, 0, 28, 28);
    app.setUserFeedbackMessage();
    app.hasDrawn = false;
};
/**
 * Post the user entered data to the server.
 */
app.save = function () {
    if (!!!app.hasDrawn) {
        return;
    }
    imgDataUrl = app.previewCanvas.toDataURL('image/png');
    xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState === 4) {
            // check HTTP status
            response = JSON.parse(xhr.responseText);
            response.imgDataUrl = imgDataUrl;
            response.target = app.currentNumber;
            app.reset();
            app.setUserFeedbackMessage(response);
        }
    };
    xhr.open('POST', '/img/save', true);
    xhr.send(JSON.stringify({
        number: app.currentNumber,
        img: imgDataUrl
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
var elementTypes = {
    NONE: 0,
    SEGMENT: 1,
    REGION: 2,
    POLYLINE: 3
};
var modeNames = ['NONE', 'SEGMENT', 'REGION', 'POLYLINE'];
var defaultColors = ['black', '#8000FF', '#22FF00', '#00BCFF'];

var mousebtn = {
    LEFT: 1,
    MIDDLE: 2,
    RIGHT: 3
}

var markCanvas = document.getElementById("image-editor");
var animCanvas = document.getElementById("animation");
var segmentButton = document.getElementById("segment");
var regionButton = document.getElementById("region");
var polylineButton = document.getElementById("polyline");
var nextButton = document.getElementById("next");

var markContext = markCanvas.getContext("2d");
var animContext = animCanvas.getContext("2d");
markContext.lineWidth = 4;
animContext.lineWidth = 4;
var selectionMode = elementTypes.NONE;

var prevX = -1, prevY = -1, currX, currY;
var rect = markCanvas.getBoundingClientRect();
var borderWidth = 1, pointRadius = 4;
var deleteButtonHTML = '<button class="btn btn-default"><strong>X</strong></button>'
var empty_markdown = 1, callCounter = 0;
var elements = {};

/*
if (elements.length > 0) {
    for (var i = 0; i < elements.length; i++) {
        // отрисовка уже размеченных объектов
    }
}
*/

animCanvas.addEventListener('mouseup', clickProcessing, false);
animCanvas.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    animCanvas.width = animCanvas.width;
    animCanvas.removeEventListener('mousemove', follow, false);
    prevX = -1;
    prevY = -1;
    return false;
}, false);
segmentButton.addEventListener('click', function () {
	setSelectionMode(elementTypes.SEGMENT);
}, false);
regionButton.addEventListener('click', function () {
	setSelectionMode(elementTypes.REGION);
}, false);
polylineButton.addEventListener('click', function () {
	setSelectionMode(elementTypes.POLYLINE);
}, false);
nextButton.addEventListener('click', sendMarkdown, false);

function clickProcessing (e) {
    if (e.which == mousebtn.LEFT) {
        currX = Math.round(e.clientX - rect.left - borderWidth);
        currY = Math.round(e.clientY - rect.top - borderWidth);

        if ((prevX != -1) && (prevY != -1)) {
            switch (selectionMode) {
                case elementTypes.SEGMENT:
                    drawLine(markContext, prevX, prevY, currX, currY, defaultColors[selectionMode]);
                    // elements.push({type: segment, path: linePath([startX, startY, endX, endY])});

                    prevX = -1;
                    prevY = -1;
                    animCanvas.removeEventListener('mousemove', follow, false);
                    break;
                case elementTypes.REGION:
                    drawRect(markContext, prevX, prevY, currX, currY, defaultColors[selectionMode]);
                    // elements.push({type: region, path: rectPath([start])});

                    prevX = -1;
                    prevY = -1;
                    animCanvas.removeEventListener('mousemove', follow, false);
                    break;
                case elementTypes.POLYLINE:
                    drawLine(markContext, prevX, prevY, currX, currY, defaultColors[selectionMode]);
                    // elements.push({type: polyline, path: linePath([startX, startY, endX, endY])});

                    prevX = currX;
                    prevY = currY;
                    break;
            }
        } else {
            prevX = currX;
            prevY = currY;
            animCanvas.addEventListener('mousemove', follow, false);
        }

        // $("ul").append('<li class="list-group-item"> New item' + deleteButtonHTML + '</li');
    }
}

// TODO: line should be thicker (may be)
function follow (e) {
    animCanvas.width = animCanvas.width;

    mouseX = e.clientX - rect.left - borderWidth;
    mouseY = e.clientY - rect.top - borderWidth;

    switch (selectionMode) {
        case elementTypes.SEGMENT:
        case elementTypes.POLYLINE:
            drawLine(animContext, prevX, prevY, mouseX, mouseY, defaultColors[selectionMode]);
            break;
        case elementTypes.REGION:
            drawRect(animContext, prevX, prevY, mouseX, mouseY, defaultColors[selectionMode]);
            break;
    }
}

function sendMarkdown () {
    // TODO: better path building
    if (!empty_markdown)
    {
    	var id = window.location.pathname;
    	var target = "/image" + id + "/markdown";
    	var xmlhttp = new XMLHttpRequest();
    	var markdown = JSON.stringify(elements);

    	xmlhttp.open('POST', target, true);
    	xmlhttp.setRequestHeader('content-type', 'application/json');
    	xmlhttp.setRequestHeader('content-length', markdown.length);
    	xmlhttp.send(markdown);

    	// TODO: check response ({msg: "ok"})
    }
}

function setSelectionMode (mode) {
    selectionMode = mode;
    document.getElementById("mode").innerHTML = 'Selection mode:' + modeNames[selectionMode];
}

function drawPoint (context, pointX, pointY, radius, pointColor) {
    context.fillStyle = pointColor;
    context.beginPath();
    context.arc(pointX, pointY, radius, 0, 2 * Math.PI, true);
    context.closePath();
    context.fill();
}

function drawLine (context, startX, startY, endX, endY, lineColor) {
    if (!((startX == endX) && (startY == endY))) {
        context.strokeStyle = lineColor;
        context.beginPath();
        context.moveTo(startX, startY);
        context.lineTo(endX, endY);
        context.closePath();
        context.stroke();
    }
}

function drawRect (context, startX, startY, endX, endY, lineColor) {
    if (!((startX == endX) || (startY == endY))) {
        context.strokeStyle = lineColor;
        var left = Math.min(startX, endX);
        var top = Math.min(startY, endY);
        var width = Math.abs(endX - startX);
        var height = Math.abs(endY - startY);
        context.strokeRect(left, top, width, height);
    }
}
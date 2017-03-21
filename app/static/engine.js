var elementTypes = {
    NONE: 0,
    SEGMENT: 1,
    REGION: 2,
    POLYLINE: 3
};
var modeNames = ['NONE', 'SEGMENT', 'REGION', 'POLYLINE'];
var defaultColors = ['black', 'red', 'green', 'blue'];

var mousebtn = {
    LEFT: 1,
    MIDDLE: 2,
    RIGHT: 3
}

var canvas = document.getElementById("image-editor");
var segmentButton = document.getElementById("segment");
var regionButton = document.getElementById("region");
var polylineButton = document.getElementById("polyline");
var nextButton = document.getElementById("next");

var context = canvas.getContext("2d");
var selectionMode = elementTypes.NONE;

var prevX, prevY, currX, currY, draw = 0;
var rect = canvas.getBoundingClientRect();
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

canvas.addEventListener('mouseup', clickProcessing, false);
canvas.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    // tempCanvas.width = tempCanvas.width;
    // tempCanvas.removeEventListener('mousemove', follow, false);
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

// FIX: somehow this function is called twice for each click on the canvas
function clickProcessing (e) {
    callCounter++;
    console.log(callCounter);
    if (e.which == mousebtn.LEFT) {
        currX = Math.round(e.clientX - rect.left - borderWidth);
        currY = Math.round(e.clientY - rect.top - borderWidth);

        if (draw) {
            switch (selectionMode) {
                case elementTypes.SEGMENT:
                    drawLine(prevX, prevY, currX, currY, 'red');
                    draw = 0;
                    // elements.push({type: segment, path: linePath([startX, startY, endX, endY])});
                    break;
                case elementTypes.REGION:
                    drawRect(prevX, prevY, currX, currY, 'green');
                    draw = 0;
                    // elements.region.push({type: region, path: rectPath()});
                    break;
                case elementTypes.POLYLINE:
                    drawLine(prevX, prevY, currX, currY, 'blue');
                    // elements.push({type: polyline, path: linePath([startX, startY, endX, endY])});
                    break;
            }
        } else {
            draw = 1;
            // addEventListener for animation
        }

        prevX = currX;
        prevY = currY;
        // $("ul").append('<li class="list-group-item"> New item' + deleteButtonHTML + '</li');
    } else {
        return false;
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

function drawPoint (pointX, pointY, radius, pointColor) {
    context.fillStyle = pointColor;
    context.beginPath();
    context.arc(pointX, pointY, radius, 0, 2 * Math.PI, true);
    context.closePath();
    context.fill();
}

function drawLine (startX, startY, endX, endY, lineColor) {
    if (!((startX == endX) && (startY == endY))) {
        context.strokeStyle = lineColor;
        context.beginPath();
        context.moveTo(startX, startY);
        context.lineTo(endX, endY);
        context.closePath();
        context.stroke();
    }
}

function drawRect (startX, startY, endX, endY, lineColor) {
    if (!((startX == endX) || (startY == endY))) {
        context.strokeStyle = lineColor;
        var left = Math.min(startX, endX);
        var top = Math.min(startY, endY);
        var width = Math.abs(endX - startX);
        var height = Math.abs(endY - startY);
        context.strokeRect(left, top, width, height);
    }
}
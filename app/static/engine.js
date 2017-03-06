var elementTypes = {
    NONE: 0,
    POINT: 1,
    SEGMENT: 2,
    RECTANGLE: 3
};

var canvas = document.getElementById("image-editor");
var pointButton = document.getElementById("point");
var segmentButton = document.getElementById("segment");
var regionButton = document.getElementById("region");
var nextButton = document.getElementById("next");

var context = canvas.getContext("2d");
var selectionMode = elementTypes.NONE;

var rect = canvas.getBoundingClientRect();
var borderWidth = 1;

var elements = {point: [], segment: [], region: []};

canvas.addEventListener('mousedown', startElement, false);
canvas.addEventListener('mouseup', endElement, false);
pointButton.addEventListener('click', function () {
	setSelectionMode(elementTypes.POINT);
}, false);
segmentButton.addEventListener('click', function () {
	setSelectionMode(elementTypes.SEGMENT);
}, false);
regionButton.addEventListener('click', function () {
	setSelectionMode(elementTypes.REGION);
}, false);
nextButton.addEventListener('click', sendMarkdown, false);

var startX, startY;

function startElement (e) {
    switch (selectionMode)
    {
        case elementTypes.SEGMENT:
        case elementTypes.REGION:
            startX = Math.round(e.clientX - rect.left - borderWidth);
            startY = Math.round(e.clientY - rect.top - borderWidth);
            break;
        default:
            break;
    }
}

function endElement (e) {
    endX = Math.round(e.clientX - rect.left - borderWidth);
    endY = Math.round(e.clientY - rect.top - borderWidth);

    switch (selectionMode)
    {
        case elementTypes.POINT:
            context.fillStyle = 'green';
            context.beginPath();
            context.arc(endX, endY, 4, 0, 2 * Math.PI, true);
            context.closePath();
            context.fill();
            elements.point.push({x: endX, y: endY});
            break;
        case elementTypes.SEGMENT:
            if (!((startX == endX) && (startY == endY)))
            {
                context.strokeStyle = 'red';
                context.beginPath();
                context.moveTo(startX, startY);
                context.lineTo(endX, endY);
                context.closePath();
                context.stroke();
                elements.segment.push({start: {x: startX, y: startY}, end: {x: endX, y: endY}});
            }
            break;
        case elementTypes.REGION:
            if (!((startX == endX) || (startY == endY)))
            {
                context.strokeStyle = 'blue';
                var left = Math.min(startX, endX);
                var top = Math.min(startY, endY);
                var width = Math.abs(endX - startX);
                var height = Math.abs(endY - startY);
                context.strokeRect(left, top, width, height);
                elements.region.push({left: left, top: top, width: width, height: height});
            }
            break;
    }
}

function sendMarkdown () {
    // TODO: better path building
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

function setSelectionMode (mode) {
    selectionMode = mode;
}
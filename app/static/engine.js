var elementTypes = {
    NONE: 0,
    SEGMENT: 1,
    REGION: 2,
    POLYLINE: 3
};
var modeNames = ['NONE', 'SEGMENT', 'REGION', 'POLYLINE'];
var defaultColors = ['black', '#ffed79', '#5ce032', '#00BCFF'];
var LEFT_MOUSE_BUTTON = 1;
var LINE_WIDTH = 4;

var markCanvas = document.getElementById("markdown");
var animCanvas = document.getElementById("animation");
var activeCanvas = document.getElementById("active-element");
var segmentButton = document.getElementById("segment");
var regionButton = document.getElementById("region");
var polylineButton = document.getElementById("polyline");
var nextButton = document.getElementById("next");

var markContext = markCanvas.getContext("2d");
var animContext = animCanvas.getContext("2d");
var selectionMode = elementTypes.NONE;

var prevX = -1, prevY = -1, currX, currY, polyline_points = [];
var rect = markCanvas.getBoundingClientRect();
var borderWidth = 1, pointRadius = 4, current_id = 0;

drawAll(markContext);

function formPattern (lineColor) {
    var pattern = document.createElement("canvas");
    p.width = 8;
    p.height = 8;
    var patternContext = pattern.getContext("2d");

    patternContext.strokeStyle = lineColor;
    patternContext.lineWidth = 2;
    patternContext.beginPath();
    patternContext.moveTo(8, 0);
    patternContext.lineTo(0, 8);
    patternContext.closePath();
    patternContext.stroke();

    return pattern;
}

animCanvas.addEventListener('mouseup', clickProcessing, false);
animCanvas.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    animCanvas.removeEventListener('mousemove', follow, false);
    clearAll(animCanvas);
    if ((selectionMode == elementTypes.POLYLINE) && (polyline_points.length > 1)) {
        var description = '(' + polyline_points[0].x + ', ' + polyline_points[0].y + ') ... (' +
                          polyline_points.slice(-1)[0].x + ', ' + polyline_points.slice(-1)[0].y + ')';
        $("ul").append('<li class="list-group-item"> Polyline<br><span class="coords">' + description + '</span>' + deleteButtonHTML(current_id) + '</li');
        elements[current_id] = {type: "polyline", path: polyline_points};
        current_id++;
        // document.getElementById("mode").innerHTML = JSON.stringify(elements);
    }

    polyline_points = [];
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

$(".list-group").on('click', '.delete-element', function(){
    var id = this.id;
    $(this).closest('.list-group-item').remove();

    delete elements[id];
    // document.getElementById("mode").innerHTML = JSON.stringify(elements);
    clearAll(markCanvas);
    drawAll(markContext);
});

function clickProcessing (e) {
    if (e.which == LEFT_MOUSE_BUTTON) {
        currX = Math.round(e.clientX - rect.left - borderWidth);
        currY = Math.round(e.clientY - rect.top - borderWidth);

        if ((prevX != -1) && (prevY != -1)) {
            switch (selectionMode) {
                case elementTypes.SEGMENT:
                    if (!((currX == prevX) && (currY == prevY))) {
                        var info = drawLine(markContext, prevX, prevY, currX, currY, defaultColors[selectionMode]);
                        elements[current_id] = {type: "segment", path: info[0]};
                        $("ul").append('<li class="list-group-item"> Segment<br><span class="coords">' + info[1] + '</span>' + deleteButtonHTML(current_id) + '</li>');
                        current_id++;
                    }

                    prevX = -1;
                    prevY = -1;
                    animCanvas.removeEventListener('mousemove', follow, false);
                    clearAll(animCanvas);
                    break;
                case elementTypes.REGION:
                    if (!((currX == prevX) || (currY == prevY))) {
                        var info = drawRect(markContext, prevX, prevY, currX, currY, defaultColors[selectionMode]);
                        elements[current_id] = {type: "region", path: info[0]};
                        $("ul").append('<li class="list-group-item"> Region<br><span class="coords">' + info[1] + '</span>' + deleteButtonHTML(current_id) + '</li>');
                        current_id++;
                    }

                    prevX = -1;
                    prevY = -1;
                    animCanvas.removeEventListener('mousemove', follow, false);
                    clearAll(animCanvas);
                    break;
                case elementTypes.POLYLINE:
                    if (!((currX == prevX) && (currY == prevY))) {
                        drawLine(markContext, prevX, prevY, currX, currY, defaultColors[selectionMode]);
                        polyline_points.push({x: currX, y: currY});

                        prevX = currX;
                        prevY = currY;
                    }
                    break;
            }
            // document.getElementById("mode").innerHTML = JSON.stringify(elements);
        } else {
            prevX = currX;
            prevY = currY;
            if (selectionMode == elementTypes.POLYLINE) {
                polyline_points.push({x: currX, y: currY});
            }
            animCanvas.addEventListener('mousemove', follow, false);
        }
    }
}

// TODO: line should be thicker (may be)
function follow (e) {
    clearAll(animCanvas);

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
    if (Object.keys(elements).length > 0)
    {
    	var id = window.location.pathname;
    	var target = "/image" + id + "/markdown";
    	var xmlhttp = new XMLHttpRequest();
    	var markdown = JSON.stringify(elements);

    	xmlhttp.open('POST', target, true);
    	xmlhttp.setRequestHeader('content-type', 'application/json; charset=UTF-8');
    	xmlhttp.setRequestHeader('content-length', markdown.length);
    	xmlhttp.send(markdown);

    	// TODO: check response ({msg: "ok"})
    }
}

function setSelectionMode (mode) {
    selectionMode = mode;
    document.getElementById("mode").innerHTML = 'Selection mode: ' + modeNames[selectionMode];
}

function drawPoint (context, pointX, pointY, radius, pointColor) {
    context.fillStyle = pointColor;
    context.arc(pointX, pointY, radius, 0, 2 * Math.PI, true);
    context.fill();
}

function drawLine (context, startX, startY, endX, endY, lineColor) {
    context.strokeStyle = lineColor;
    context.lineWidth = LINE_WIDTH;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.beginPath();
    context.moveTo(startX, startY);
    context.lineTo(endX, endY);
    context.closePath();
    context.stroke();
    return [[{x: startX, y: startY}, {x: endX, y: endY}],
            '(' + startX + ', ' + startY + ') - (' + endX + ', ' + endY + ')'];
}

function drawRect (context, startX, startY, endX, endY, lineColor) {
    context.strokeStyle = lineColor;
    context.lineWidth = LINE_WIDTH;
    context.lineCap = "round";
    var left = Math.min(startX, endX);
    var top = Math.min(startY, endY);
    var width = Math.abs(endX - startX);
    var height = Math.abs(endY - startY);
    context.strokeRect(left, top, width, height);
    return [[{x: left, y: top}, {x: left + width, y: top},
            {x: left + width, y: top + height}, {x: left, y: top + height}, {x: left, y: top}],
            '(' + left + ', ' + top + ') - ' + width + 'x' + height];
}

function drawAll (context) {
    for (var id in elements) {
        switch (elements[id].type) {
            case "segment":
                selectionMode = elementTypes.SEGMENT;
                break;
            case "region":
                selectionMode = elementTypes.REGION;
                break;
            case "polyline":
                selectionMode = elementTypes.POLYLINE;
                break;
        }
        context.strokeStyle = defaultColors[selectionMode];
        context.lineWidth = LINE_WIDTH;
        context.lineCap = "round";
        context.lineJoin = "round";
        context.beginPath();
        context.moveTo(elements[id].path[0].x, elements[id].path[0].y);
        for (var number = 1; number < elements[id].path.length; number++) {
            context.lineTo(elements[id].path[number].x, elements[id].path[number].y);
        }
        context.closePath();
        context.stroke();
    }
}

function clearAll (canvas) {
    canvas.width = canvas.width;
}

function deleteButtonHTML (id) {
    return '<button class="btn btn-default delete-element" id="' + id +
           '"><span class="glyphicon glyphicon-remove"></span></button>';
}
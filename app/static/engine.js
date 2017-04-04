//  Passed from Flask in 'main.html' template:
//     - elements - container for markdown
//     - image_src - URL of the image

// TODO:
//   - dragging
//   - highlighting element on corresponding <li> hover

var elementTypes = {
    NONE: 0,
    SEGMENT: 1,
    REGION: 2,
    POLYLINE: 3
};
var elementNames = ['', 'Segment', 'Region', 'Polyline'];
var defaultColors = ['black', '#ffed79', '#5ce032', '#00BCFF'];
var LEFT_MOUSE_BUTTON = 1, LINE_WIDTH = 4, RELATIVE_SCALE = 0.25;
var MIN_POSSIBLE_SCALE = 0.2, MAX_POSSIBLE_SCALE = 5;

var selectionMode = elementTypes.NONE;
var prev = new Point(-1, -1), curr, innerOffset, outerOffset, polyline_points = [];
var borderWidth = 1, pointRadius = 4, scale, current_id = 0;

var imageCanvas = document.getElementById("image");
var imageContext = imageCanvas.getContext("2d");
var markCanvas = document.getElementById("markdown");
var markContext = markCanvas.getContext("2d");
var animCanvas = document.getElementById("animation");
var animContext = animCanvas.getContext("2d");
var activeCanvas = document.getElementById("active-element");
var segmentButton = document.getElementById("segment");
var regionButton = document.getElementById("region");
var polylineButton = document.getElementById("polyline");
var nextButton = document.getElementById("next");
var zoomInButton = document.getElementById("zoom-in");
var zoomOutButton = document.getElementById("zoom-out");

var imageObj = new Image();
imageObj.onload = function () {
    var rect = imageCanvas.getBoundingClientRect();
    outerOffset = new Point(rect.left, rect.top);
    var initialScale = Math.min(imageCanvas.width / imageObj.width, imageCanvas.height / imageObj.height);
    scale = initialScale;
    redraw(scale, true);
}
imageObj.src = image_src;

animCanvas.addEventListener('mouseup', clickProcessing, false);
animCanvas.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    animCanvas.removeEventListener('mousemove', follow, false);
    clearCanvas(animCanvas);
    if ((selectionMode == elementTypes.POLYLINE) && (polyline_points.length > 1)) {
        $("ul").append(generateLi(current_id));
        elements[current_id] = {type: "polyline", path: polyline_points};
        current_id++;
        // document.getElementById("mode").innerHTML = JSON.stringify(elements);
    }

    polyline_points = [];
    prev.x = -1;
    prev.y = -1;
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
zoomOutButton.addEventListener('click', function () {
    if (scale < MAX_POSSIBLE_SCALE)
        scale /= (1 + RELATIVE_SCALE);
    redraw(scale, false);
}, false);
zoomInButton.addEventListener('click', function () {
    if (scale > MIN_POSSIBLE_SCALE)
        scale *= (1 + RELATIVE_SCALE);
    redraw(scale, false);
}, false);

function clickProcessing (e) {
    if (e.which == LEFT_MOUSE_BUTTON) {
        curr = coords(e);

        if ((prev.x != -1) && (prev.y != -1)) {
            switch (selectionMode) {
                case elementTypes.SEGMENT:
                    if (!((curr.x == prev.x) && (curr.y == prev.y))) {
                        var info = drawLine(markContext, prev, curr, defaultColors[selectionMode], true);
                        elements[current_id] = {type: "segment", path: info};
                        $("ul").append(generateLi(current_id));
                        current_id++;
                    }

                    prev.x = -1;
                    prev.y = -1;
                    animCanvas.removeEventListener('mousemove', follow, false);
                    clearCanvas(animCanvas);
                    break;
                case elementTypes.REGION:
                    if (!((curr.x == prev.x) || (curr.y == prev.y))) {
                        var info = drawRect(markContext, prev, curr, defaultColors[selectionMode], true);
                        elements[current_id] = {type: "region", path: info};
                        $("ul").append(generateLi(current_id));
                        current_id++;
                    }

                    prev.x = -1;
                    prev.y = -1;
                    animCanvas.removeEventListener('mousemove', follow, false);
                    clearCanvas(animCanvas);
                    break;
                case elementTypes.POLYLINE:
                    if (!((curr.x == prev.x) && (curr.y == prev.y))) {
                        drawLine(markContext, prev, curr, defaultColors[selectionMode], true);
                        polyline_points.push({x: curr.cs().x, y: curr.cs().y});

                        prev.x = curr.x;
                        prev.y = curr.y;
                    }
                    break;
            }
            // document.getElementById("mode").innerHTML = JSON.stringify(elements);
        } else {
            prev.x = curr.x;
            prev.y = curr.y;
            if (selectionMode == elementTypes.POLYLINE) {
                polyline_points.push({x: curr.cs().x, y: curr.cs().y});
            }
            animCanvas.addEventListener('mousemove', follow, false);
        }
    }
}

function follow (e) {
    clearCanvas(animCanvas);

    mouse = coords(e);

    switch (selectionMode) {
        case elementTypes.SEGMENT:
        case elementTypes.POLYLINE:
            drawLine(animContext, prev, mouse, defaultColors[selectionMode], false);
            break;
        case elementTypes.REGION:
            drawRect(animContext, prev, mouse, defaultColors[selectionMode], false);
            break;
    }
}

function sendMarkdown () {
    var id = window.location.pathname;    // "/<int>"
    var target = "/image" + id + "/markdown";
    var xmlhttp = new XMLHttpRequest();
    var markdown = JSON.stringify(elements);

    xmlhttp.open('POST', target, true);
    xmlhttp.setRequestHeader('content-type', 'application/json; charset=UTF-8');
    xmlhttp.setRequestHeader('content-length', markdown.length);
    xmlhttp.send(markdown);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {
            console.log(xmlhttp.responseText);    // empty instead of '{"msg" : "ok"}'
        }
    }
}

function setSelectionMode (mode) {
    selectionMode = mode;
    document.getElementById("mode").innerHTML = 'Selection mode: ' + elementNames[selectionMode];
}

function drawPoint (context, point, radius, pointColor) {
    context.fillStyle = pointColor;
    context.arc(point.x, point.y, radius, 0, 2 * Math.PI, true);
    context.fill();
}

function drawLine (context, start, end, lineColor, need_to_center) {
    context.strokeStyle = lineColor;
    context.lineWidth = LINE_WIDTH;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.beginPath();
    if (need_to_center) {
        start = start.cs();
        end = end.cs();
    }
    context.moveTo(start.x, start.y);
    context.lineTo(end.x, end.y);
    context.closePath();
    context.stroke();
    return [{x: start.x, y: start.y}, {x: end.x, y: end.y}];
}

function drawRect (context, start, end, lineColor, need_to_center) {
    context.strokeStyle = lineColor;
    context.lineWidth = LINE_WIDTH;
    context.lineCap = "round";
    if (need_to_center) {
        start = start.cs();
        end = end.cs();
    }
    var left = Math.min(start.x, end.x);
    var top = Math.min(start.y, end.y);
    var width = Math.abs(end.x - start.x);
    var height = Math.abs(end.y - start.y);
    context.strokeRect(left, top, width, height);
    return [{x: left, y: top}, {x: left + width, y: top},
            {x: left + width, y: top + height}, {x: left, y: top + height}, {x: left, y: top}];
}

function drawAll (context, build_list) {
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

        if (build_list) {
            $("ul").append(generateLi(id));
        }
    }
}

function clearCanvas (canvas) {
    canvas.width = canvas.width;
}

function formPattern (lineColor) {
    var pattern = document.createElement("canvas");
    pattern.width = 8;
    pattern.height = 8;
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

$(".list-group").on('click', '.delete-element', function(){
    var id = this.id;
    $(this).closest('.list-group-item').remove();

    delete elements[id];
    // document.getElementById("mode").innerHTML = JSON.stringify(elements);
    markContext.clearRect(-image.width / 2, -image.height / 2, image.width, image.height);
    drawAll(markContext, false);
});

function generateLi (id) {
    liHTML = '<li class="list-group-item">';
    liHTML += elementNames[selectionMode];
    liHTML += '<button class="btn btn-default delete-element" id="' + id +
              '"><span class="glyphicon glyphicon-remove"></span></button>'; + '</li>';
    return liHTML;
}

function redraw (scale, load) {
    imageCanvas.width = imageCanvas.width;
    imageContext.setTransform(scale, 0, 0, scale, imageCanvas.width / 2, imageCanvas.height / 2);
    imageContext.drawImage(imageObj, - imageObj.width / 2, - imageObj.height / 2);

    markCanvas.width = markCanvas.width;
    markContext.setTransform(scale, 0, 0, scale, markCanvas.width / 2, markCanvas.height / 2);
    if (load) {
        drawAll(markContext, true);
    } else {
        drawAll(markContext, false);
    }

    innerOffset = new Point(markCanvas.width / 2, markCanvas.height / 2);
}

function coords (e) {
    x = e.pageX - outerOffset.x - borderWidth;
    y = e.pageY - outerOffset.y - borderWidth;
    return new Point(x, y);
}

function Point (x, y) {
    this.x = x;
    this.y = y;
}
Point.prototype.c = function () {
    return new Point(this.x - innerOffset.x, this.y - innerOffset.y);
}
Point.prototype.s = function () {
    return new Point(Math.round(this.x / scale), Math.round(this.y / scale));
}
Point.prototype.cs = function () {
    return this.c().s();
}
Point.prototype.dist = function (other) {
    dx = this.x - other.x;
    dy = this.y - other.y;
    return Math.sqrt(x * x + y * y);
}
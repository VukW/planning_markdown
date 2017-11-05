/*  Passed from Flask in 'main.html' template:
 *     - elements - container for the markdown
 *     - image_src - URL of the image
 *
 *
 *  TODO:
 *     - close polylines
 *     - adding tags to marked elements
 */

var elementTypes = {
    NONE: 0,
    SEGMENT: 1,
    REGION: 2,
    POLYLINE: 3
};
var elementSubtypes = {
    NONE: 0,
    WINDOW: 1,
    WALL: 2,
    DOOR: 3
};
var keys = {
    SHIFT: 16,
    SPACE: 32,
    UP: 38,
    DOWN: 40,
    A: 65,
    C: 67,
    X: 88,
    Z: 90
};
var elementNames = ['', 'Segment', 'Region', 'Polyline'];
var defaultColors = ['black', '#ffed79', '#5ce032', '#00bcff'];
var auxiliaryColors = ['black', '#fff4ae', '#acf694', '#aee3f6'];
var LEFT_MOUSE_BUTTON = 1, LINE_WIDTH = 2, HIGHLIGHT_VALUE = 0.95, RELATIVE_SCALE = 0.25;
var MIN_POSSIBLE_SCALE = 0.2, MAX_POSSIBLE_SCALE = 5, POINT_RADIUS = 8;

var selectionMode = elementTypes.NONE;
var prev = new Point(-1, -1), curr;
var innerOffset, outerOffset, polyline_points = [];
var scale, current_id = 0, drag = 0, drawAlong = 0;

var imageCanvas = document.getElementById("image");
imageCanvas.width = window.innerWidth * 5 / 6;
imageCanvas.height = window.innerHeight;
var imageContext = imageCanvas.getContext("2d");

var markCanvas = document.getElementById("markdown");
markCanvas.width = imageCanvas.width;
markCanvas.height = imageCanvas.height;
var markContext = markCanvas.getContext("2d");

var animCanvas = document.getElementById("animation");
animCanvas.width = imageCanvas.width;
animCanvas.height = imageCanvas.height;
var animContext = animCanvas.getContext("2d");

var activeCanvas = document.getElementById("active-element");
activeCanvas.width = imageCanvas.width;
activeCanvas.height = imageCanvas.height;
var activeContext = activeCanvas.getContext("2d");

var nextButton = document.getElementById("next");
var duplicateButton = document.getElementById("duplicate");
var zoomInButton = document.getElementById("zoom-in");
var zoomOutButton = document.getElementById("zoom-out");
var areaInput = document.getElementById("area");

var imageObj = new Image();
imageObj.onload = function () {
    var rect = imageCanvas.getBoundingClientRect();
    outerOffset = new Point(rect.left, rect.top);
    var initialScale = Math.min(imageCanvas.width / imageObj.width, imageCanvas.height / imageObj.height);
    scale = initialScale;
    innerOffset = new Point(markCanvas.width / 2, markCanvas.height / 2);
    if (!("area" in elements)) {
        elements.area = 0.0;
    }
    areaInput.value = 0.0;
    redraw(true);
}
imageObj.src = image_src;

document.addEventListener('keydown', function (e) {
    if (e.which == keys.SHIFT) {
        drag = 1;
    }
}, false);

document.addEventListener('keyup', function (e) {
    switch (e.which) {
        case keys.SHIFT:
            drag = 0;
            break;
        case keys.A:
            drawAlong = !drawAlong;
            break;
        case keys.C:
            $("#polyline").click();
            break;
        case keys.X:
            $("#region").click();
            break;
        case keys.Z:
            $("#segment").click();
            break;
        case keys.SPACE:
            e.preventDefault();
            nextButton.click();
            break;
        case keys.UP:
            e.preventDefault();
            zoomInButton.click();
            break;
        case keys.DOWN:
            e.preventDefault();
            zoomOutButton.click();
            break;
    }
})

animCanvas.addEventListener('mousedown', function (e) {
    if (drag) {
        prev = coords(e);
    }
}, false);
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
    clearCanvas(activeCanvas);
    prev.x = -1;
    prev.y = -1;
    return false;
}, false);

$('input[name="mode"]:radio').change(function () {
    switch (this.id) {
        case "segment":
            setSelectionMode(elementTypes.SEGMENT);
            break;
        case "region":
            setSelectionMode(elementTypes.REGION);
            break;
        case "polyline":
            setSelectionMode(elementTypes.POLYLINE);
            break;
    }
});
nextButton.addEventListener('click', sendMarkdown, false);
duplicateButton.addEventListener('click', preventDuplicate, false);
zoomOutButton.addEventListener('click', function () {
    innerOffset = new Point(markCanvas.width / 2, markCanvas.height / 2);
    if (scale > MIN_POSSIBLE_SCALE)
        scale /= (1 + RELATIVE_SCALE);
    redraw(false);
}, false);
zoomInButton.addEventListener('click', function () {
    innerOffset = new Point(markCanvas.width / 2, markCanvas.height / 2);
    if (scale < MAX_POSSIBLE_SCALE)
        scale *= (1 + RELATIVE_SCALE);
    redraw(false);
}, false);
areaInput.addEventListener('change', function () {
    elements.area = areaInput.value;
}, false);

function clickProcessing (e) {
    if (e.which == LEFT_MOUSE_BUTTON) {
        curr = coords(e);

        if ((prev.x != -1) && (prev.y != -1)) {
            if (drag) {
                innerOffset.x += (curr.x - prev.x);
                innerOffset.y += (curr.y - prev.y);
                redraw(false);

                prev.x = -1;
                prev.y = -1;
            } else {
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
                            elements[current_id] = {type: "region", subtype: "rect_wall", path: info};
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
                        /*
                            console.log(curr.cs().x + ' ' + curr.cs().y);
                            console.log(curr.cs().dist(polyline_points[0]));
                            if (curr.cs().dist(polyline_points[0]) < POINT_RADIUS) {
                                var beginning = new Point(polyline_points[0].x, polyline_points[0].y)
                                drawLine(markContext, prev, beginning, defaultColors[selectionMode], true);
                                polyline_points.push({x: polyline_points[0].x, y: polyline_points[0].y});

                                $("ul").append(generateLi(current_id));
                                elements[current_id] = {type: "polyline", path: polyline_points};
                                current_id++;
                                prev.x = -1;
                                prev.y = -1;

                                animCanvas.removeEventListener('mousemove', follow, false);
                                clearCanvas(activeCanvas);
                            } else {*/
                                drawLine(markContext, prev, curr, defaultColors[selectionMode], true);
                                polyline_points.push({x: curr.cs().x, y: curr.cs().y});

                                prev.x = curr.x;
                                prev.y = curr.y;
                            // }
                        }
                        break;
                }
                // document.getElementById("mode").innerHTML = JSON.stringify(elements);
            }
        } else {
            prev.x = curr.x;
            prev.y = curr.y;
            if (selectionMode == elementTypes.POLYLINE) {
                polyline_points.push({x: curr.cs().x, y: curr.cs().y});
                //drawPoint(activeContext, curr, POINT_RADIUS, defaultColors[elementTypes.POLYLINE]);
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

function preventDuplicate () {
    var id = window.location.pathname;
    var target = "/image" + id + "/duplicate?duplicate=true";
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.open('POST', target, true);
    xmlhttp.send('warning');
}

function setSelectionMode (mode) {
    selectionMode = mode;
    document.getElementById("mode").innerHTML = 'Mode: ' + elementNames[selectionMode].toUpperCase();
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
        if (id != "area") {
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
            if ((selectionMode == elementTypes.REGION) && !("subtype" in elements[id])) {
                elements[id].subtype = "rect_wall";
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
            context.stroke();
            context.closePath();

            if (build_list) {
                $("ul").append(generateLi(id));
                if (selectionMode == elementTypes.REGION) {
                    $("#" + id).closest(".list-group-item").children(".subtype-select").val(elements[id].subtype).change();
                }
            }
        }
    }
}

function clearCanvas (canvas) {
    canvas.width = canvas.width;
}

function highlight (id) {
    activeContext.setTransform(scale, 0, 0, scale, innerOffset.x, innerOffset.y);
    activeContext.globalAlpha = HIGHLIGHT_VALUE;

    switch (elements[id].type) {
        case "segment":
            activeContext.strokeStyle = defaultColors[elementTypes.SEGMENT];
            activeContext.fillStyle = auxiliaryColors[elementTypes.SEGMENT];
            break;
        case "region":
            activeContext.strokeStyle = defaultColors[elementTypes.REGION];
            activeContext.fillStyle = auxiliaryColors[elementTypes.REGION];
            break;
        case "polyline":
            activeContext.strokeStyle = defaultColors[elementTypes.POLYLINE];
            activeContext.fillStyle = auxiliaryColors[elementTypes.POLYLINE];
            break;
    }

    activeContext.lineWidth = LINE_WIDTH;
    activeContext.lineCap = "round";
    activeContext.lineJoin = "round";
    activeContext.beginPath();
    activeContext.moveTo(elements[id].path[0].x, elements[id].path[0].y);
    for (var number = 1; number < elements[id].path.length; number++) {
        activeContext.lineTo(elements[id].path[number].x, elements[id].path[number].y);
    }
    activeContext.stroke();
    activeContext.closePath();
    activeContext.fill();
}

$(".list-group").on('click', '.delete-element', function () {
    var id = this.id;
    $(this).closest('.list-group-item').remove();

    delete elements[id];
    // document.getElementById("mode").innerHTML = JSON.stringify(elements);
    markContext.clearRect(-image.width / 2, -image.height / 2, image.width, image.height);
    clearCanvas(activeCanvas);
    drawAll(markContext, false);
});

$(".list-group").on('mouseenter', '.list-group-item', function () {
    var id = $(this).children(".delete-element").attr("id");
    highlight(id);
});

$(".list-group").on('mouseleave', '.list-group-item', function () {
    clearCanvas(activeCanvas);
});

$(".list-group").on('change', '.subtype-select', function () {
    var id = $(this).closest(".list-group-item").children(".delete-element").attr("id");
    elements[id].subtype = $(this).val();
})

function generateLi (id) {
    liHTML = '<li class="list-group-item ' + elementNames[selectionMode].toLowerCase() + '-item sharp">';
    liHTML += elementNames[selectionMode];
    if (selectionMode == elementTypes.REGION) {
        liHTML += '<br><select class="subtype-select">' +
                  '<option value="rect_wall">Wall</option>' +
                  '<option value="rect_window">Window</option>' +
                  '<option value="rect_door">Door</option></select>';
    }
    liHTML += '<button class="btn btn-default delete-element" id="' + id +
              '"><span class="glyphicon glyphicon-remove"></span></button>'; + '</li>';
    return liHTML;
}

function redraw (load) {
    imageCanvas.width = imageCanvas.width;
    imageContext.setTransform(scale, 0, 0, scale, innerOffset.x, innerOffset.y);
    imageContext.drawImage(imageObj, - imageObj.width / 2, - imageObj.height / 2);

    markCanvas.width = markCanvas.width;
    markContext.setTransform(scale, 0, 0, scale, innerOffset.x, innerOffset.y);
    if (load) {
        drawAll(markContext, true);
    } else {
        drawAll(markContext, false);
    }

    document.getElementById("zoom").innerHTML = 'Zoom: ' + Math.round(100 * scale) + '%';
}

function coords (e) {
    x = e.pageX - outerOffset.x;
    y = e.pageY - outerOffset.y;
    if ((drawAlong) && (prev.x != -1) && (prev.y != -1)) {
        dx = Math.abs(x - prev.x);
        dy = Math.abs(y - prev.y);
        x = (dx > dy) ? x : prev.x;
        y = (dx > dy) ? prev.y : y;
    }
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
    return Math.sqrt(dx * dx + dy * dy);
}
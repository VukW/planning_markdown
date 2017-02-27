var canvas = document.getElementById("image-editor");
var borderWidth = 1;
var context = canvas.getContext("2d");
var points_marked = [];

var rect = canvas.getBoundingClientRect();

canvas.addEventListener('mousedown', function(e) {
    var canvasX = e.clientX - rect.left - borderWidth;
    var canvasY = e.clientY - rect.top - borderWidth;

    points_marked.push({canvasX, canvasY});

    context.fillStyle = "green";
    context.beginPath();
    context.arc(canvasX, canvasY, 5, 0, 2 * Math.PI, true);
    context.closePath();
    context.fill();
}, false);

function displayEnd() {
    alert("Done!");
}
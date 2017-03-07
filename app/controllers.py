from app import app, db, images
from io import BytesIO
from flask import send_file, redirect, jsonify, request, abort, Blueprint, render_template, url_for
from os import listdir

main_page_module = Blueprint('main_page', __name__, url_prefix='/')


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route('/image/<int:image_id>')
def get_image(image_id):
        image_id = image_id
        return serve_pil_image(images[image_id].image)


def get_next_image_id(start=-1):
    for image_id in range(start + 1, 1000000):
        if images[image_id].markdown == {}:
            return image_id


@app.route('/next')
def next_image_id():
    image_id = get_next_image_id()
    if image_id is not None:
        return jsonify(next_unmarked_picture=image_id)
    return abort("no unmarked pictures found")


@app.route('/next/<int:start_id>')
def next_image_id_offset(start_id):
    image_id = get_next_image_id(start_id)
    if image_id is not None:
        return jsonify(next_unmarked_picture=image_id)
    return abort("no unmarked pictures found")


@app.route('/image/<int:image_id>/markdown', methods=['GET', 'POST'])
def already_saved_markdown(image_id):
    if request.method == 'GET':
        return jsonify(images[image_id].markdown)
    elif request.method == 'POST':
        images[image_id].markdown = request.get_json(force=True)
    return jsonify(msg="ok")


@app.route('/image/all/markdown')
def all_saved_markdowns():
    return jsonify(db.all())


@app.route('/')
def root():
    next_image_id_ = get_next_image_id()
    return redirect('/'+str(next_image_id_))


@app.route('/<int:image_id>')
def main(image_id):
    return render_template("main.html",
                           image_id=image_id,
                           image_id_prev=image_id - 1 if image_id > 0 else None,
                           image_id_next=get_next_image_id(image_id),
                           markdown=images[image_id].markdown)


@app.route('/ls/<path:varargs>')
def ls(varargs=None):
    if varargs == '0':
        varargs = ''
    varargs = '/' + varargs
    return jsonify(listdir(varargs))
from app import app, db, images
from io import BytesIO
from flask import send_file, redirect, jsonify, request, abort, Blueprint, render_template
from config import NEXT_UNMARKED_ONLY

main_page_module = Blueprint('main_page', __name__, url_prefix='/')


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route('/image/<int:image_id>/duplicate', methods=['GET', 'POST'])
def get_duplicate(image_id):
    if request.method == 'GET':
        return images[image_id].duplicate
    elif request.method == 'POST':
        if 'duplicate' not in request.args:
            return abort('duplicate param is obligatory here')
        duplicate = request.args['duplicate']
        duplicate = (duplicate.lower().strip() in ['t', 'true'])
        images[image_id].duplicate = duplicate
        return jsonify(msg="ok")


@app.route('/image/<int:image_id>')
def get_image(image_id):
    return serve_pil_image(images[image_id].image)


def get_next_image_id(start=-1):
    for image_id in range(start + 1, db.max_id + 1):
        image = images[image_id]
        if ((not image.locked)
                and (not NEXT_UNMARKED_ONLY or (image.markdown == {}))
                and not image.duplicate):
            return image_id
    return 0


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
    image = images[image_id]
    if request.method == 'GET':
        return jsonify(image.markdown)
    elif request.method == 'POST':
        image.markdown = request.get_json(force=True)
        image.remove_lock()
    return jsonify(msg="ok")


@app.route('/image/all/markdown')
def all_saved_markdowns():
    return jsonify(db.all())


@app.route('/')
def root():
    next_image_id_ = get_next_image_id()
    return redirect('/' + str(next_image_id_))


@app.route('/<int:image_id>')
def main(image_id):
    image = images[image_id]
    image.set_lock()
    return render_template("main.html",
                           image_id=image_id,
                           image_id_prev=image_id - 1 if image_id > 0 else None,
                           image_id_next=get_next_image_id(image_id),
                           markdown=image.markdown)

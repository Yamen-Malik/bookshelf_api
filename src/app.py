from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import re
from models import *

app = Flask(__name__)
setup_db(app)

BOOKS_PER_PAGE = 10


def paginate(page: int, books: list):
    """ Formats and paginate the given list according to the given page number
      page: the page number
      questions : list to paginate
      Retutns: list of dictionaries
    """
    start_index = (page - 1) * BOOKS_PER_PAGE
    books = [b.short_format() for b in books]
    return books[start_index: start_index + BOOKS_PER_PAGE]

# -----------------------
#       Books
# -----------------------


@app.route("/books")
def get_books():
    genre = request.args.get("genre", None, type=str)
    search_term = request.args.get("search_term", None, type=str)
    books_query = Book.query
    if genre:
        books_query = books_query.join(
            BookGenre, Book.id == BookGenre.book_id).filter(BookGenre.genre.ilike(genre))

    if search_term:
        books_query = books_query.filter(Book.title.ilike(f"%{search_term}%"))

    books = books_query.order_by(Book.title).all()

    page = request.args.get("page", 1, type=int)
    return jsonify({
        "success": True,
        "books": paginate(page, books),
        "total": len(books)
    })


@app.route("/books", methods=["POST"])
def create_book():
    data = request.json
    if not data:
        abort(400)
    try:
        title = data["title"].strip()
        description = data["description"].strip()
        genres = data["genres"]
        author_id = data["author"].strip()
        pages = data["pages"].strip()
        year = data["year"].strip()
    except:
        # if the body doesn't contain all the required data raise bad request error
        abort(400)

    if not (title and description and genres and pages and year) or not author_id.isnumeric():
        # if the body has an empty string then raise unprocessable entity error
        abort(422)
    elif Book.query.filter(Book.title.ilike(title)).first():
        # if the book already exists raise conflict error
        abort(409)

    # check if author exists
    author_id = int(author_id)
    if not Author.query.filter_by(id=author_id).first():
        abort(404)

    # add book
    book = Book(title, description, author_id, pages, year)
    book.insert()

    # Add genres
    for genre in genres:
        BookGenre(book.id, genre).insert()

    return jsonify({
        "success": True,
        "created": book.id
    }), 201


@app.route("/books/<id>")
def get_book_details(id):
    return jsonify(Book.get(id).long_format())


@app.route("/books/<id>", methods=["DELETE"])
def delete_book(id):
    book = Book.get(id)

    # delete book genres
    for g in BookGenre.query.filter_by(book_id=book.id).all():
        g.delete()

    # then delete the book
    book.delete()
    return jsonify({
        "success": True,
        "deleted": id
    })


# -----------------------
#       Authors
# -----------------------

@app.route("/authors")
def get_authors():
    search_term = request.args.get("search_term", None, type=str)
    authors_query = Author.query
    if search_term:
        authors_query = authors_query.filter(
            Author.name.ilike(f"%{search_term}%"))

    authors = authors_query.order_by(Author.name).all()
    page = request.args.get("page", 1, type=int)
    return jsonify({
        "success": True,
        "authors": paginate(page, authors),
        "total": len(authors)
    })


@app.route("/authors", methods=["POST"])
def create_author():
    data = request.json
    if not data:
        abort(400)
    try:
        name = data["name"].strip()
        description = data["description"].strip()
        birthday = data["birthday"].strip()
    except:
        # if the body doesn't contain all the required data raise bad request error
        abort(400)

    if not (name and description and birthday):
        # if the body has an empty string then raise unprocessable entity error
        abort(422)
    elif Author.query.filter(Author.name.ilike(name)).first():
        # if the author already exists raise conflict error
        abort(409)

    try:
        # try to parse the birthday into a datetime object
        date = re.split("/|-", birthday)
        birthday = datetime.datetime(*map(int, date))
    except:
        abort(422)

    author = Author(name, description, birthday)
    author.insert()
    return jsonify({
        "success": True,
        "created": author.id
    }), 201


@app.route("/authors/<id>")
def get_author_details(id):
    return jsonify(Author.get(id).long_format())


@app.route("/authors/<id>", methods=["DELETE"])
def delete_author(id):
    author = Author.get(id)

    # if the author have books riase conflict error
    if Book.query.filter_by(author_id=author.id).first():
        abort(409)

    # else delete author
    author.delete()
    return jsonify({
        "success": True,
        "deleted": id
    })

# region Error Handling


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(405)
def not_allowed_method(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(409)
def conflict(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "conflict"
    }), 409


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

# @app.errorhandler(AuthError)
# def auth_error(error):
#     return jsonify({
#         "success": False,
#         "error": error.status_code,
#         "message": error.error["description"]
#     }), error.status_code

# endregion


if __name__ == "__main__":
    app.run(debug=True)

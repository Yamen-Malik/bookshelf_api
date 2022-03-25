from flask import Flask, request, abort, jsonify, redirect
import datetime
import re
from auth import get_token_from_code, requires_auth, AuthError, get_user_id, get_login_url
from models import *


def create_app():
    app = Flask(__name__)
    setup_db(app)

    # region BOOKS

    @app.route("/books")
    def get_books():
        genre = request.args.get("genre", type=str)
        search_term = request.args.get("search_term", type=str)
        books_query = Book.query
        if genre:
            books_query = books_query.join(
                BookGenre, Book.id == BookGenre.book_id).filter(BookGenre.genre.ilike(genre))

        if search_term:
            books_query = books_query.filter(
                Book.title.ilike(f"%{search_term}%"))

        books = books_query.all()

        return jsonify({
            "success": True,
            "books": paginate(books),
            "total": len(books)
        })

    @app.route("/books", methods=["POST"])
    @requires_auth("post:books")
    def create_book():
        data = request.json
        try:
            title = data["title"].strip()
            description = data["description"].strip()
            genres = data["genres"]
            author_id = data["author_id"]
            pages = data["pages"]
            year = data["year"]
        except:
            # if the body doesn't contain all the required data raise bad request error
            abort(400)

        if not (title and description and year and author_id.isnumeric() and pages.isnumeric() and type(genres) == list):
            # if the body has an empty string or invalid numeric value then raise unprocessable entity error
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
        return jsonify({
            "success": True,
            "book": Book.get(id).detailed_format()
        })

    @app.route("/books/<id>", methods=["PATCH"])
    @requires_auth("patch:books")
    def edit_book(id):
        book = Book.get(id)
        data = request.json
        if not data:
            abort(400)

        try:
            # check if author exists
            author_id = int(data.get("author_id", book.author_id))
            if not Author.query.filter_by(id=author_id).first():
                abort(404)

            # update book data
            book.title = data.get("title", book.title).strip()
            book.description = data.get(
                "description", book.description).strip()
            book.author_id = author_id
            book.pages = data.get("pages", book.pages)
            book.year = data.get("year", book.year)
            book.update()

            # get new genres
            new_genres = data.get("genres")
            if new_genres and not type(new_genres) == list:
                raise Exception
        except:
            db.session.rollback()
            abort(422)

        # update genres
        old_genres = [
            g.genre for g in BookGenre.query.filter_by(book_id=id).all()]
        if new_genres and new_genres != old_genres:
            for genre in (old_genres + new_genres):
                if genre not in old_genres:
                    BookGenre(book.id, genre).insert()
                elif genre not in new_genres:
                    BookGenre.query.filter_by(
                        book_id=id, genre=genre).first().delete()

        return jsonify({
            "success": True
        }), 204

    @app.route("/books/<id>", methods=["DELETE"])
    @requires_auth("delete:books")
    def delete_book(id):
        book = Book.get(id)

        # delete book genres
        for g in BookGenre.query.filter_by(book_id=book.id).all():
            g.delete()

        for stored_book in Stored_Book.query.filter_by(book_id=book.id).all():
            stored_book.delete()
        # then delete the book
        book.delete()
        return jsonify({
            "success": True,
            "deleted": id
        })

    # endregion

    # region AUTHORS

    @app.route("/authors")
    def get_authors():
        search_term = request.args.get("search_term", type=str)
        authors_query = Author.query
        if search_term:
            authors_query = authors_query.filter(
                Author.name.ilike(f"%{search_term}%"))

        authors = authors_query.all()
        return jsonify({
            "success": True,
            "authors": paginate(authors),
            "total": len(authors)
        })

    @app.route("/authors", methods=["POST"])
    @requires_auth("post:authors")
    def create_author():
        data = request.json
        try:
            name = data["name"].strip()
            description = data["description"].strip()
            birthday = data["birthday"]
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
        return jsonify({
            "success": True,
            "author": Author.get(id).detailed_format()
        })

    @app.route("/authors/<id>", methods=["PATCH"])
    @requires_auth("patch:authors")
    def edit_author(id):
        author = Author.get(id)
        data = request.json
        if not data:
            abort(400)

        try:
            # update author data
            author.name = data.get("name", author.name).strip()
            author.description = data.get(
                "description", author.description).strip()
            birthday = data.get("birthday")

            if birthday:
                # try to parse the birthday into a datetime object
                date = re.split("/|-", birthday)
                birthday = datetime.datetime(*map(int, date))
                author.birthday = birthday

            author.update()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({
            "success": True
        }), 204

    @app.route("/authors/<id>", methods=["DELETE"])
    @requires_auth("delete:authors")
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

    # endregion

    # region USER ACCOUNT

    @app.route("/login")
    def login():
        return redirect(get_login_url())

    @app.route("/callback")
    def callback():
        # handles response from auth0 authorize endpoint

        # get authorization code
        code = request.args.get("code", type=str)
        token = get_token_from_code(code)
        user_id = get_user_id(token)

        # add the default shelves if the user doesn't have shelves
        if Shelf.query.filter_by(user_id=user_id).count() == 0:
            Shelf(user_id, "want to read").insert()
            Shelf(user_id, "currently reading").insert()
            Shelf(user_id, "read").insert()

        return jsonify({
            "success": True,
            "token": token
        })

    @app.route("/user")
    @requires_auth()
    def user():
        return jsonify({
            "success": True,
            "user_id": get_user_id()
        })

    # endregion

    # region SHELVES

    @app.route("/shelves")
    @requires_auth()
    def get_shelves():
        user_id = get_user_id()
        shelves = Shelf.query.filter_by(user_id=user_id).all()

        return jsonify({
            "success": True,
            "shelves": paginate(shelves),
            "total": len(shelves)
        })

    @app.route("/shelves", methods=["POST"])
    @requires_auth()
    def create_shelf():
        try:
            name = request.json["name"].strip()
        except:
            abort(400)
        if not name:
            # if the name is empty then raise unprocessable entity error
            abort(422)

        user_id = get_user_id()
        if Shelf.query.filter_by(user_id=user_id).filter(Shelf.name.ilike(name)).first():
            # if the shelf already exists raise conflict error
            abort(409)

        shelf = Shelf(user_id, name)
        shelf.insert()
        return jsonify({
            "success": True,
            "created": shelf.user_based_id
        }), 201

    @app.route("/shelves/<id>")
    @requires_auth()
    def get_shelf_details(id):
        return jsonify({
            "success": True,
            "shelf": Shelf.get(get_user_id(), id).detailed_format()
        })

    @app.route("/shelves/<id>", methods=["PATCH"])
    @requires_auth()
    def edit_shelf(id):
        shelf = Shelf.get(get_user_id(), id)
        try:
            name = request.json["name"].strip()
        except:
            abort(400)
        
        if not name:
            abort(422)
        
        shelf.name = name
        shelf.update()
        return jsonify({
            "success": True
        }), 204


    @app.route("/shelves/<id>", methods=["DELETE"])
    @requires_auth()
    def delete_shelf(id):
        shelf = Shelf.get(get_user_id(), id)

        # delete stored books in the shelf
        for book in Stored_Book.query.filter_by(shelf_id=shelf.id).all():
            book.delete()

        # then delete the shelf
        shelf.delete()
        return jsonify({
            "success": True,
            "deleted": id
        })

    # ---------------------------
    #       Storing Books
    # ---------------------------

    @app.route("/shelves/<shelf_id>", methods=["POST"])
    @requires_auth()
    def add_book_to_shelf(shelf_id):
        try:
            book_id = int(request.json.get("book_id"))
        except AttributeError:
            abort(400)
        except ValueError:
            abort(422)

        user_id = get_user_id()
        shelf = Shelf.get(user_id, shelf_id)
        if Stored_Book.query.filter_by(user_id=user_id, book_id=book_id).first():
            # if the book is already stored in any of the user's shleves raise conflict error
            abort(409)

        Stored_Book(user_id, shelf.id, book_id).insert()

        return jsonify({
            "success": True
        })

    @app.route("/shelves/<shelf_id>/<book_id>", methods=["DELETE"])
    @requires_auth()
    def remove_book_from_shelf(shelf_id, book_id):
        Stored_Book.get(get_user_id(), book_id).delete()
        return jsonify({
            "success": True
        })

    # endregion

    # region ERROR HANDLERS

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

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error["description"]
        }), error.status_code

    # endregion

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()

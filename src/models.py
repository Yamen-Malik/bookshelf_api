from flask import abort, request
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Sequence
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from constants import ITEMS_PER_PAGE, DB_PATH

# using string.capwords because str.title() misbehaves with apostrophes
from string import capwords

db = SQLAlchemy()

def setup_db(app, database_path=DB_PATH):
    """
        binds a flask application and a SQLAlchemy service
    """
    if not database_exists(DB_PATH):
        create_database(DB_PATH)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def paginate(l: list):
    """ Formats and paginate the given list according to page number in the request arguments
      l : list to paginate
      Returns: list of dictionaries
    """
    page = request.args.get("page", 1, type=int)
    start_index = (page - 1) * ITEMS_PER_PAGE
    l = [e.format() for e in l]
    return l[start_index: start_index + ITEMS_PER_PAGE]


class DatabaseObject():
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get(cls, id: int):
        """ Returns an instance with the given id
            id : the id of the desired instance
        """
        try:
            id = int(id)
        except ValueError:
            # if the id isn't an integer raise a not found error
            abort(404)

        instance = cls.query.filter_by(id=id).first()
        if not instance:
            abort(404)
        return instance

# region Tabels


class Book(db.Model, DatabaseObject):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    pages = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    def __init__(self, title, description, author_id, pages, year):
        self.title = capwords(title)
        self.description = description
        self.author_id = author_id
        self.pages = pages
        self.year = year

    def get_genres(self):
        return [r.genre for r in BookGenre.query.filter_by(book_id=self.id).all()]

    def format(self):
        return {
            "id": self.id,
            "title": self.title,
            "genres": self.get_genres(),
            "author": {
                "name": Author.query.filter_by(id=self.author_id).first().name,
                "id": self.author_id
            }
        }

    def detailed_format(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "genres": self.get_genres(),
            "pages": self.pages,
            "year": self.year,
            "author": {
                "name": Author.query.filter_by(id=self.author_id).first().name,
                "id": self.author_id
            }
        }


class Author(db.Model, DatabaseObject):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)

    def __init__(self, name, description, birthday):
        self.name = capwords(name)
        self.description = description
        self.birthday = birthday

    def format(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def detailed_format(self):
        books = Book.query.filter_by(author_id=self.id).all()
        formatted_books = paginate(books)
        genres = set()
        for format in formatted_books:
            del format["author"]
            genres.update(format["genres"])

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "books": formatted_books,
            "total_books": len(books),
            "genres": list(genres),
            "birthday": str(self.birthday)
        }


class BookGenre(db.Model, DatabaseObject):
    __tablename__ = "book_genres"

    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    genre = Column(String, primary_key=True)

    def __init__(self, book_id, genre):
        self.book_id = book_id
        self.genre = capwords(genre)

    def format(self):
        return {
            "book_id": self.book_id,
            "type": self.genre
        }


class Shelf(db.Model, DatabaseObject):
    __tablename__ = "shelves"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    user_based_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.user_based_id = Shelf.query.filter_by(user_id=user_id).count()+1

    def format(self):
        total_books = Stored_Book.query.filter_by(shelf_id=self.id).count()
        return {
            "id": self.user_based_id,
            "name": self.name,
            "total_books": total_books
        }

    def detailed_format(self):
        books = []
        for id in db.session.query(Stored_Book.book_id).filter_by(shelf_id=self.id).all():
            books.append(Book.get(id.book_id))

        return {
            "id": self.user_based_id,
            "name": self.name,
            "books": paginate(books),
            "total_books": len(books)
        }

    # overwrite DatabaseObject.get to use the user_based_id instead of id
    def get(user_id: str, id: int):
        """ Returns an instance with the given ids
            user_id: the user id of the shelf owner
            id : the id of the desired shelf
        """
        try:
            id = int(id)
        except ValueError:
            # if the id isn't an integer raise a not found error
            abort(404)

        instance = Shelf.query.filter_by(
            user_id=user_id, user_based_id=id).first()
        if not instance:
            abort(404)
        return instance


class Stored_Book(db.Model, DatabaseObject):
    __tablename__ = "stored_books"

    user_id = Column(String, primary_key=True)
    shelf_id = Column(Integer, ForeignKey("shelves.id"))
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)

    def __init__(self, user_id, shelf_id, book_id):
        self.user_id = user_id
        self.shelf_id = shelf_id
        self.book_id = book_id

    def format(self):
        return {
            "book": self.book.format(),
            "shelf": self.shelf_id
        }

    # overwrite DatabaseObject.get to use the user_id, shelf_id and book_id to get the instance
    def get(user_id: str, book_id: int):
        """ Returns an instance with the given ids
            user_id: the user id of the shelves owner
            book_id : the book id
        """
        try:
            book_id = int(book_id)
        except ValueError:
            # if the id isn't an integer raise a not found error
            abort(404)

        instance = Stored_Book.query.filter_by(
            user_id=user_id, book_id=book_id).first()
        if not instance:
            abort(404)
        return instance

# endregion

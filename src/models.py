from os import getenv
from flask import abort
from sqlalchemy import Column, String, Integer, Date, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database

# using string.capwords because str.title() misbehaves with apostrophes
from string import capwords

database_name = "bookshelf_api"
database_path = "postgresql://{}:{}@{}/{}".format(
    getenv("DB_USER"),
    getenv("DB_PASSWORD"),
    getenv("DB_HOST"),
    database_name)
if not database_exists(database_path):
    create_database(database_path)
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    """
        binds a flask application and a SQLAlchemy service
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


# region Tabels
class Book(db.Model):
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

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_genres(self):
        return [r.genre for r in BookGenre.query.filter_by(book_id=self.id).all()]

    def short_format(self):
        return {
            "id": self.id,
            "title": self.title,
            "genres": self.get_genres(),
            "author": {
                "name": Author.query.filter_by(id=self.author_id).first().name,
                "id": self.author_id
            }
        }

    def long_format(self):
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

    def get(id):
        if type(id) != int and not id.isnumeric():
            abort(400)
        id = int(id)
        book = Book.query.filter_by(id=id).first()
        if not book:
            abort(404)
        return book


class Author(db.Model):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)

    def __init__(self, name, description, birthday):
        self.name = capwords(name)
        self.description = description
        self.birthday = birthday

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short_format(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def long_format(self):
        # genres = [r.genre for r in AuthorGenre.query.filter_by(author_id=self.id).all()]
        books = []
        genres = set()
        for book in Book.query.filter_by(author_id=self.id).all():
            format = book.short_format()
            del format["author"]
            del format["author_id"]
            books.append(format)
            genres.update(format["genres"])

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "books": books,
            "genres": list(genres),
            "birthday": str(self.birthday)
        }

    def get(id):
        if type(id) != int and not id.isnumeric():
            abort(400)
        id = int(id)
        author = Author.query.filter_by(id=id).first()
        if not author:
            abort(404)
        return author


class BookGenre(db.Model):
    __tablename__ = "book_genres"

    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    genre = Column(String, primary_key=True)

    def __init__(self, book_id, genre):
        self.book_id = book_id
        self.genre = capwords(genre)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "book_id": self.book_id,
            "type": self.genre
        }

# endregion

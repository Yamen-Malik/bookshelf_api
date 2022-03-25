import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","src")))
from app import create_app
from models import *

#* REMEBER: load the data from the sql file to the database before running the tests
# command: psql -U myUsername bookshelf_test < bookshelf_test_data.sql
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            os.getenv("DB_USER"),
            os.getenv("DB_PASSWORD"),
            os.getenv("DB_HOST"),
            self.database_name)
        setup_db(self.app, self.database_path)

        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # Create all tables
            self.db.create_all()

        # Get jwt tokens
        self.manager_auth_header = {
            "Authorization": "Bearer " + os.getenv("MANAGER_JWT")}
        self.librarian_auth_header = {
            "Authorization": "Bearer " + os.getenv("LIBRARIAN_JWT")}

        # Data for a test book to send to the api
        self.added_book_id = None
        self.new_book = {
            "title": "test book title",
            "description": "test book description",
            "author_id": "2",
            "pages": "3",
            "year": "1999",
            "genres": ["g1", "g2", "g3"]
        }

        # Data for a test author to send to the api
        self.added_author_id = None
        self.new_author = {
            "name": "test author name",
            "description": "test author description",
            "birthday": "1970-1-1"
        }

        # Store the book data before deleting it
        self.book_to_delete_id = 2
        res = self.client().get(f"/books/{self.book_to_delete_id}")
        data = json.loads(res.data)
        self.deleted_book = data["book"]
        self.deleted_book["author_id"] = data["book"]["author"]["id"]

        # Store the author data before deleting it
        self.author_to_delete_id = 2
        res = self.client().get(f"/authors/{self.author_to_delete_id}")
        data = json.loads(res.data)
        self.deleted_author = data["author"]

    
    def tearDown(self):
        """Executed after each test"""
        
        try:
            # add the deleted book
            if not Book.query.filter_by(id=self.book_to_delete_id).first():
                title = self.deleted_book["title"]
                description = self.deleted_book["description"]
                author_id = self.deleted_book["author_id"]
                pages = self.deleted_book["pages"]
                year = self.deleted_book["year"]
                genres = self.deleted_book["genres"]
                book = Book(title, description, author_id, pages, year)
                book.id = self.book_to_delete_id
                book.insert()
                for genre in genres:
                    BookGenre(self.book_to_delete_id, genre).insert()
            
            # add the deleted author
            if not Author.query.filter_by(id=self.author_to_delete_id).first():
                name = self.deleted_author["name"]
                description = self.deleted_author["description"]
                birthday = self.deleted_author["birthday"]
                author = Author(name, description, birthday)
                author.id = self.author_to_delete_id
                author.insert()            

        except Exception as err:
            print("Unable to add the deleted book/author back to the database")
            print(err)

        # delete the added test book and author
        try:
            if self.added_book_id:
                for book_genre in BookGenre.query.filter_by(book_id=self.added_book_id).all():
                    book_genre.delete()
                Book.get(self.added_book_id).delete()
            
            if self.added_author_id:
                Author.get(self.added_author_id).delete()
            
        except Exception as err:
            print("Unable to delete the test book/author from the database")
            print(err)
            pass

    # region Books

    #GET /books
    def test_get_books(self):
        res = self.client().get("/books")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total"])
        self.assertTrue(len(data["books"]))

    def test_405_get_books(self):
        res = self.client().delete("/books")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    # POST /books

    def test_create_new_book(self):
        res = self.client().post("/books", json=self.new_book,
                                 headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.added_book_id = int(data.get("created"))

    def test_401_create_new_book(self):
        res = self.client().post("/books", json=self.new_book)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_400_create_new_book(self):
        res = self.client().post("/books", headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    #GET /books/<id>

    def test_get_book_details(self):
        res = self.client().get("/books/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["book"]["author"])
        self.assertTrue(data["book"]["id"])
        self.assertTrue(data["book"]["description"])
        self.assertTrue(data["book"]["pages"])
        self.assertTrue(data["book"]["year"])
        self.assertTrue(len(data["book"]["genres"]))

    def test_404_get_book_details(self):
        res = self.client().get("/books/10000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # PATCH /books/<id>

    def test_patch_book(self):
        data = {"title": "patched title"}
        res = self.client().patch("/books/1", json=data, headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_422_patch_book(self):
        data = {"year": "year"}
        res = self.client().patch("/books/1", json=data, headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    # DELETE /books/<id>

    def test_delete_book(self):
        res = self.client().delete(
            f"/books/{self.book_to_delete_id}", headers=self.manager_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(int(data["deleted"]), self.book_to_delete_id)

    def test_403_delete_book(self):
        res = self.client().delete("/books/1", headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data["success"], False)

    def test_404_delete_book(self):
        res = self.client().delete("/books/10000", headers=self.manager_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # endregion

    # region Authors

    #GET /authors
    def test_get_authors(self):
        res = self.client().get("/authors")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total"])
        self.assertTrue(len(data["authors"]))

    def test_405_get_authors(self):
        res = self.client().delete(f"/authors", headers=self.manager_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    # POST /authors

    def test_create_new_author(self):
        res = self.client().post("/authors", json=self.new_author,
                                 headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.added_author_id = data.get("created")

    def test_401_create_new_author(self):
        res = self.client().post("/authors", json=self.new_author)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_400_create_new_author(self):
        res = self.client().post("/authors", headers=self.manager_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    #GET /authors/<id>

    def test_get_author_details(self):
        res = self.client().get(f"/authors/2")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["author"]["name"])
        self.assertTrue(data["author"]["id"])
        self.assertTrue(data["author"]["description"])
        self.assertTrue(data["author"]["birthday"])
        self.assertTrue(len(data["author"]["books"]))
        self.assertTrue(len(data["author"]["genres"]))

    def test_404_get_author_details(self):
        res = self.client().get(f"/authors/10000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # PATCH /authors/<id>

    def test_patch_author(self):
        data = {"name": "patched name"}
        res = self.client().patch(f"/authors/4", json=data,
                                  headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_422_patch_author(self):
        data = {"birthday": "2000 jan,2"}
        res = self.client().patch(f"/authors/4", json=data,
                                  headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    # DELETE /authors/<id>

    def test_409_delete_author(self):
        res = self.client().delete(
            f"/authors/{self.author_to_delete_id}", headers=self.manager_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 409)
        self.assertEqual(data["success"], False)
        # self.assertEqual(data["deleted"], self.author_to_delete_id)

    def test_401_delete_author(self):
        res = self.client().delete(f"/authors/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_404_delete_author(self):
        res = self.client().delete(f"/authors/10000", headers=self.manager_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # endregion

    # region Shelves

    # GET /shelves
    def test_get_shelves(self):
        res = self.client().get("/shelves", headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total"])
        self.assertTrue(len(data["shelves"]))
    
    def test_405_get_shelves(self):
        res = self.client().patch("/shelves", headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)

    def test_401_create_new_shelf(self):
        res = self.client().post("/shelves", json=self.new_book)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_400_create_new_self(self):
        res = self.client().post("/shelves", headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")
 
    # GET /shelves/<id>
    def test_get_shelf_details(self):
        res = self.client().get("/shelves/1", headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["shelf"]["id"])
        self.assertTrue(data["shelf"]["name"])
        self.assertEqual(type(data["shelf"]["books"]), list)
        self.assertIsNotNone(data["shelf"]["total_books"])

    def test_404_get_shelf_details(self):
        res = self.client().get("/shelves/10000", headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # PATCH /shelves/<id>
    def test_patch_shelf(self):
        data = {"name": "READ"}
        res = self.client().patch("/shelves/3", json=data, headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
   
    def test_400_patch_shelf(self):
        res = self.client().patch("/shelves/3", headers=self.librarian_auth_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
    

    # endregion

if __name__ == "__main__":
    unittest.main()

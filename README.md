# Bookshelf API 
### Installing Dependencies

1. **Python 3** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


3. **PIP Dependencies** - install dependencies by running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages within the `requirements.txt` file.

### Authorization Setup
This API uses [Auth0](https://auth0.auth0.com/) to handle Authorization   
to setup and link your Auth0 account with the API fill your client credentials in [src/.env](src/.env)  
and the api audience in [constants.py](src/constants.py)

### Database Setup
Add your psql database user,password and host to [src/.env](src/.env)

### Running the server

Within `./src` directory run following commands:

```bash
export FLASK_APP=app.py
flask run --reload
```
The `--reload` flag will detect file changes and restart the server automatically.

### Testing
To setup the tests you need to create two JWTs for two roles:

1. **Manager** with following permissions:  
`post:books` `patch:books` `delete:books` `post:authors` `patch:authors` `delete:authors`

2. **Librarian** with the following permissions:  
`post:books` `patch:books` `post:authors` `patch:authors`

and place them in [testing/.env](testing/.env)

then create the testing database and load its tables and data by navigating to the testing folder and running:
```bash
createdb bookshelf_test
psql bookshelf_test < bookshelf_test_data.sql
```
Then to test the API, run:
```bash
python tests.py
```
If the previous command didn't work try using 
```bash
python3 tests.py
```

# Getting Started
## Base URL
By default the app will be hosted at:
`http://127.0.0.1:5000/`


## Error Handling
The API uses default http error codes and returns errors as JSON objects  
### **Sample**:
```json
{
    "error": 404,
    "message": "not found",
    "success": false
}
```

## Pagination
All the data returned by the API will be paginated in groups of 10.  
Use the query parameter `page` to set the page number.

**Example:** `/books?page=1`

# Endpoints

## GET /books
**Description**: Fetches all the books in the database

**Query parameters**: 
- `page`
- `search_term`
- `genre`

**Returns**:
- `books` **List** of `Objects` that contain:
    - `id` **Integer** book id
    - `title` **String** book title
    -  `author` **Object** that contains:
        - `id` **Integer** author id
        - `name` **String** author name
    - `genres` **List** of **Strings**
- `total` **Integer** the total number of books in the requested query
- `success` **Boolean**

**Sample**: `curl http://127.0.0.1:5000/books?search_term=Sorcerer's`
```json
{
    "books": [
        {
            "author": {
                "id": 2,
                "name": "J.K. Rowling"
            },
            "genres": [
                "Fantasy",
                "Fiction",
                "Magic"
            ],
            "id": 1,
            "title": "Harry Potter and the Sorcerer's Stone"
        },
    ],
    "success": true,
    "total": 1
}
```


## GET /books/\<id>
**Description**: Fetches the details of a book

**Returns:**
- `book` **Object** that contains: 
    - `id` **Integer** book id
    - `title` **String** book title
    - `description` **String** book description
    - `pages` **Integer** number of pages in the book
    - `year` **Integer** the year in which the book was published in
    -  `author` **Object** that contains:
        - `id` **Integer** author id
        - `name` **String** author name
    - `genres` **List** of **Strings**
- `success` **Boolean**

**Sample**: `curl 127.0.0.1:5000/books/1`
```json
{
    "book": {
        "author": {
            "id": 2,
            "name": "J.K. Rowling"
        },
        "description": "Harry Potter's life is miserable. His parents are dead and he's ...",
        "genres": [
            "Fantasy",
            "Fiction",
            "Magic"
        ],
        "id": 1,
        "pages": 309,
        "title": "Harry Potter and the Sorcerer's Stone",
        "year": 1997
    },
    "success": true
}
```

## POST /books
**Description**: Add a new book
* <span style = "color:cyan">Requires Authorization</span>
* <span style = "color:cyan">Requires Permission: `post:books`</span>

**Request Data**:
- `title` **String** book title
- `description` **String** book description
- `pages` **Integer** number of pages in the book
- `year` **Integer** the year in which the book was published in
- `author_id` **Integer** the id of the book author
- `genres` **List** of **Strings**

**Returns:**
- `created` **Integer** the id of the created book
- `success` **Boolean**

**Sample Request Body**:
```json
{
    "title" : "Harry Potter and the Prisoner of Azkaban",
    "description" : "For twelve long years, the dread fortress of Azkaban held an infamous prisoner named ...",
    "year" : "1999",
    "author_id" : "2",
    "pages" : "435",
    "genres" : ["fantasy","fiction", "magic"]
}
```
**Sample Response**:
```json
{
    "created": 3,
    "success": true
}
```


## PATCH /books/\<id>
**Description**: Edit an existing book
* <span style = "color:cyan">Requires Authorization</span>
* <span style = "color:cyan">Requires Permission: `patch:books`</span>

**Request Data** at least one of the following:
- `title` **String** book title
- `description` **String** book description
- `pages` **Integer** number of pages in the book
- `year` **Integer** the year in which the book was published in
- `author_id` **Integer** the id of the book author
- `genres` **List** of **Strings**

**Returns:**
- `success` **Boolean**

**Sample Request Body**:
```json
{
    "genres" : ["fantasy","fiction", "magic", "Young Adult"]
}
```


## DELETE /books/\<id>
**Description**: Delete a book
* <span style = "color:cyan">Requires Authorization</span>
* <span style = "color:cyan">Requires Permission: `delete:books`</span>

**Returns:**
- `deleted` **Integer** the id of the deleted book
- `success` **Boolean**


## GET /authors
**Description**: Fetches all the authors in the database

**Query parameters**: 
- `page`
- `search_term`

**Returns:**
- `authors` **List** of **Objects** that contain: 
    - `id` **Integer** author id
    - `name` **String** author name
- `total` **Integer** the total number of authors in the requested query
- `success` **Boolean**

**Sample**: `curl  127.0.0.1:5000/authors?search_term=j.k`
```json
{
    "authors": [
        {
            "id": 2,
            "name": "J.K. Rowling"
        }
    ],
    "success": true,
    "total": 1
}
```


## GET /authors/\<id>
**Description**: Fetches the details of an author

**Query parameters**: 
- `page`

**Returns:**
- `author` **Object** that contains: 
    - `id` **Integer** author id
    - `name` **String** author name
    - `description` **String** author description
    - `birthday` **String** the date of birth of the author. Format: `YY-MM-DD`
    - `books` **List** of `Objects` that contain:
        - `id` **Integer** book id
        - `title` **String** book title
        - `genres` **List** of **Strings**
    - `genres` **List** of **Strings** the books' genres that the author writes
    - `total_books` **Integer** the total number of books for the author
- `success` **Boolean**

**Sample**: `curl 127.0.0.1:5000/books/2`
```json
{
    "author": {
        "birthday": "1965-07-31",
        "books": [
            {
                "genres": [
                    "Fantasy",
                    "Fiction",
                    "Magic"
                ],
                "id": 1,
                "title": "Harry Potter and the Sorcerer's Stone"
            }
        ],
        "description": "Although she writes under the pen name J.K. Rowling, pronounced like rolling, her name ...",
        "genres": [
            "Magic",
            "Fiction",
            "Fantasy"
        ],
        "id": 2,
        "name": "J.K. Rowling",
        "total_books": 1
    },
    "success": true
}
```


## POST /authors
**Description**: Add a new author  
* <span style = "color:cyan">Requires Authorization</span>
* <span style = "color:cyan">Requires Permission: `post:authors`</span>

**Request Data**:
- `name` **String** author name
- `description` **String** author description
- `birthday` **String** the date of birth of the author. Format: `YY-MM-DD` or `YY/MM/DD`

**Returns:**
- `created` **Integer** the id of the created author
- `success` **Boolean**

**Sample Request Body**:
```json
{
    "name" : "J.K. Rowling",
    "description" : "Although she writes under the pen name J.K. Rowling, pronounced like rolling, her name ...",
    "birthday" : "1965-7-31"
}
```
**Sample Response**:
```json
{
    "created": 2,
    "success": true
}
```


## PATCH /authors/\<id>
**Description**: Edit an existing author  
* <span style = "color:cyan">Requires Authorization</span>
* <span style = "color:cyan">Requires Permission: `patch:authors`</span>

**Request Data** at least one of the following:
- `name` **String** author name
- `description` **String** author description
- `birthday` **String** the date of birth of the author. Format: `YY-MM-DD` or `YY/MM/DD`

**Returns:**
- `success` **Boolean**

**Sample Request Body**:
```json
{
    "birthday" : "1965-3-14"
}
```


## DELETE /authors/\<id>
**Description**: Delete a book
* <span style = "color:cyan">Requires Authorization</span>
* <span style = "color:cyan">Requires Permission: `delete:authors`</span>

**Returns:**
- `deleted` **Integer** the id of the deleted author
- `success` **Boolean**


## GET /shelves
**Description**: Fetches the shelves of the user
* <span style = "color:cyan">Requires Authorization</span>

**Query parameters**: 
- `page`

**Returns:**
- `shelves` **List** of **Objects** that contain: 
    - `id` **Integer** shelf id. **Unique only for the user's shelves**
    - `name` **String** shelf name
    - `total_books` **Integer** the number of books in the shelf
- `total` **Integer** the total number of shelves that the user own
- `success` **Boolean**

**Sample**: `curl -H "Authorization: TOKEN"  127.0.0.1:5000/shelves`
```json
{
    "shelves": [
        {
            "id": 1,
            "name": "want to read",
            "total_books": 0
        },
        {
            "id": 2,
            "name": "currently reading",
            "total_books": 1
        },
        {
            "id": 3,
            "name": "read",
            "total_books": 0
        }
    ],
    "success": true,
    "total": 3
}
```


## GET /shelves/\<id>
**Description**: Fetches the details of a shelf
* <span style = "color:cyan">Requires Authorization</span>

**Query parameters**: 
- `page`

**Returns:**
- `shelf` **Object** that contains: 
    - `id` **Integer** shelf id
    - `name` **String** shelf name
    - `books` **List** of `Objects` that contain:
        - `id` **Integer** book id
        - `title` **String** book title
        -  `author` **Object** that contains:
            - `id` **Integer** author id
            - `name` **String** author name
        - `genres` **List** of **Strings**
    - `total_books` **Integer** the total number of books in the shelf
- `success` **Boolean**

**Sample**: `curl -H "Authorization: TOKEN" 127.0.0.1:5000/shelves/2`
```json
{
    "shelf": {
        "books": [
            {
                "author": {
                    "id": 2,
                    "name": "J.K. Rowling"
                },
                "genres": [
                    "Fantasy",
                    "Fiction",
                    "Magic"
                ],
                "id": 1,
                "title": "Harry Potter and the Sorcerer's Stone"
            }
        ],
        "id": 2,
        "name": "currently reading",
        "total_books": 1
    },
    "success": true
}
```


## POST /shelves
**Description**: Add a new shelf
* <span style = "color:cyan">Requires Authorization</span>

**Request Data**:
- `name` **String** shelf name

**Returns:**
- `created` **Integer** the id of the created shelf
- `success` **Boolean**

**Sample Request Body**:
```json
{
    "name" : "favorites"
}
```
**Sample Response**:
```json
{
    "created": 4,
    "success": true
}
```


## PATCH /shelves/\<id>
**Description**: Add a new shelf
* <span style = "color:cyan">Requires Authorization</span>

**Request Data**:
- `name` **String** shelf name

**Returns:**
- `success` **Boolean**

**Sample Request Body**:
```json
{
    "name" : "Favorite Books"
}
```


## DELETE /shelves/\<id>
**Description**: Delete a shelf
* <span style = "color:cyan">Requires Authorization</span>

**Returns:**
- `deleted` **Integer** the id of the deleted shelf
- `success` **Boolean**

**Sample Response**:
```json
{
    "deleted": 5,
    "success": true
}
```

## POST /shelves/\<id>
**Description**: Add a book to a shelf
* <span style = "color:cyan">Requires Authorization</span>

**Request Data**:
- `book_id` **Integer**

**Returns:**
- `success` **Boolean**

**Sample Request Body**:
```json
{
    "book_id" : "1"
}
```

## DELETE /shelves/\<shelf_id>/\<book_id>
**Description**: Remove a book from a shelf
* <span style = "color:cyan">Requires Authorization</span>

**Returns:**
- `success` **Boolean**

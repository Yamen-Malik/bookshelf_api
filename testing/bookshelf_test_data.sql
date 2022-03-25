--
-- PostgreSQL database dump
--

-- Dumped from database version 12.9 (Ubuntu 12.9-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.9 (Ubuntu 12.9-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: authors; Type: TABLE; Schema: public; Owner: yamen
--

CREATE TABLE public.authors (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying NOT NULL,
    birthday date NOT NULL
);


ALTER TABLE public.authors OWNER TO yamen;

--
-- Name: authors_id_seq; Type: SEQUENCE; Schema: public; Owner: yamen
--

CREATE SEQUENCE public.authors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.authors_id_seq OWNER TO yamen;

--
-- Name: authors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yamen
--

ALTER SEQUENCE public.authors_id_seq OWNED BY public.authors.id;


--
-- Name: book_genres; Type: TABLE; Schema: public; Owner: yamen
--

CREATE TABLE public.book_genres (
    book_id integer NOT NULL,
    genre character varying NOT NULL
);


ALTER TABLE public.book_genres OWNER TO yamen;

--
-- Name: books; Type: TABLE; Schema: public; Owner: yamen
--

CREATE TABLE public.books (
    id integer NOT NULL,
    title character varying NOT NULL,
    description character varying NOT NULL,
    author_id integer NOT NULL,
    pages integer NOT NULL,
    year integer NOT NULL
);


ALTER TABLE public.books OWNER TO yamen;

--
-- Name: books_id_seq; Type: SEQUENCE; Schema: public; Owner: yamen
--

CREATE SEQUENCE public.books_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.books_id_seq OWNER TO yamen;

--
-- Name: books_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yamen
--

ALTER SEQUENCE public.books_id_seq OWNED BY public.books.id;


--
-- Name: shelves; Type: TABLE; Schema: public; Owner: yamen
--

CREATE TABLE public.shelves (
    id integer NOT NULL,
    user_id character varying,
    user_based_id integer,
    name character varying
);


ALTER TABLE public.shelves OWNER TO yamen;

--
-- Name: shelves_id_seq; Type: SEQUENCE; Schema: public; Owner: yamen
--

CREATE SEQUENCE public.shelves_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.shelves_id_seq OWNER TO yamen;

--
-- Name: shelves_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yamen
--

ALTER SEQUENCE public.shelves_id_seq OWNED BY public.shelves.id;


--
-- Name: shlef_id; Type: SEQUENCE; Schema: public; Owner: yamen
--

CREATE SEQUENCE public.shlef_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.shlef_id OWNER TO yamen;

--
-- Name: stored_books; Type: TABLE; Schema: public; Owner: yamen
--

CREATE TABLE public.stored_books (
    user_id character varying NOT NULL,
    shelf_id integer,
    book_id integer NOT NULL
);


ALTER TABLE public.stored_books OWNER TO yamen;

--
-- Name: authors id; Type: DEFAULT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.authors ALTER COLUMN id SET DEFAULT nextval('public.authors_id_seq'::regclass);


--
-- Name: books id; Type: DEFAULT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.books ALTER COLUMN id SET DEFAULT nextval('public.books_id_seq'::regclass);


--
-- Name: shelves id; Type: DEFAULT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.shelves ALTER COLUMN id SET DEFAULT nextval('public.shelves_id_seq'::regclass);


--
-- Data for Name: authors; Type: TABLE DATA; Schema: public; Owner: yamen
--

COPY public.authors (id, name, description, birthday) FROM stdin;
2	J.K. Rowling	Although she writes under the pen name J.K. Rowling, pronounced like rolling, her name when her first Harry Potter book was published was simply Joanne Rowling. Anticipating that the target audience of young boys might not want to read a book written by a woman, her publishers demanded that she use two initials, rather than her full name. As she had no middle name, she chose K as the second initial of her pen name, from her paternal grandmother Kathleen Ada Bulgen Rowling. She calls herself Jo and has said, "No one ever called me 'Joanne' when I was young, unless they were angry." Following her marriage, she has sometimes used the name Joanne Murray when conducting personal business. During the Leveson Inquiry she gave evidence under the name of Joanne Kathleen Rowling. In a 2012 interview, Rowling noted that she no longer cared that people pronounced her name incorrectly.	1965-07-31
4	Adam Savage	Adam Whitney Savage is an American industrial design and special effects designer/fabricator, actor, educator, and co-host of the Discovery Channel television series MythBusters.	1967-07-15
\.


--
-- Data for Name: book_genres; Type: TABLE DATA; Schema: public; Owner: yamen
--

COPY public.book_genres (book_id, genre) FROM stdin;
1	Fantasy
1	Fiction
1	Magic
1	Young Adult
2	Fantasy
2	Fiction
2	Magic
2	Young Adult
4	Fantasy
4	Fiction
4	Magic
4	Young Adult
5	Nonfiction
5	Biography
\.


--
-- Data for Name: books; Type: TABLE DATA; Schema: public; Owner: yamen
--

COPY public.books (id, title, description, author_id, pages, year) FROM stdin;
1	Harry Potter and the Sorcerer's Stone	Harry Potter's life is miserable. His parents are dead and he's stuck with his heartless relatives, who force him to live in a tiny closet under the stairs. But his fortune changes when he receives a letter that tells him the truth about himself: he's a wizard. A mysterious visitor rescues him from his relatives and takes him to his new home, Hogwarts School of Witchcraft and Wizardry.	2	309	1997
2	Harry Potter and the Chamber of Secrets	Ever since Harry Potter had come home for the summer, the Dursleys had been so mean and hideous that all Harry wanted was to get back to the Hogwarts School for Witchcraft and Wizardry. But just as he’s packing his bags, Harry receives a warning from a strange impish creature who says that if Harry returns to Hogwarts, disaster will strike.	2	341	1998
4	Harry Potter And The Prisoner Of Azkaban	For twelve long years, the dread fortress of Azkaban held an infamous prisoner named Sirius Black. Convicted of killing thirteen people with a single curse, he was said to be the heir apparent to the Dark Lord, Voldemort.	2	435	1999
5	Every Tool's a Hammer: Life Is What You Make It	n this New York Times bestselling “imperative how-to for creativity” (Nick Offerman), Adam Savage—star of Discovery Channel’s Mythbusters—shares his golden rules of creativity, from finding inspiration to following through and successfully making your idea a reality.	4	320	2019
\.


--
-- Data for Name: shelves; Type: TABLE DATA; Schema: public; Owner: yamen
--

COPY public.shelves (id, user_id, user_based_id, name) FROM stdin;
7	116621330057142429786	1	want to read
8	116621330057142429786	2	currently reading
9	116621330057142429786	3	read
13	620b83abb4d1ca006829c19e	1	want to read
14	620b83abb4d1ca006829c19e	2	currently reading
15	620b83abb4d1ca006829c19e	3	read
\.


--
-- Data for Name: stored_books; Type: TABLE DATA; Schema: public; Owner: yamen
--

COPY public.stored_books (user_id, shelf_id, book_id) FROM stdin;
116621330057142429786	9	2
\.


--
-- Name: authors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yamen
--

SELECT pg_catalog.setval('public.authors_id_seq', 4, true);


--
-- Name: books_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yamen
--

SELECT pg_catalog.setval('public.books_id_seq', 5, true);


--
-- Name: shelves_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yamen
--

SELECT pg_catalog.setval('public.shelves_id_seq', 15, true);


--
-- Name: shlef_id; Type: SEQUENCE SET; Schema: public; Owner: yamen
--

SELECT pg_catalog.setval('public.shlef_id', 9, true);


--
-- Name: authors authors_pkey; Type: CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT authors_pkey PRIMARY KEY (id);


--
-- Name: book_genres book_genres_pkey; Type: CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.book_genres
    ADD CONSTRAINT book_genres_pkey PRIMARY KEY (book_id, genre);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (id);


--
-- Name: shelves shelves_pkey; Type: CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.shelves
    ADD CONSTRAINT shelves_pkey PRIMARY KEY (id);


--
-- Name: stored_books stored_books_pkey; Type: CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.stored_books
    ADD CONSTRAINT stored_books_pkey PRIMARY KEY (user_id, book_id);


--
-- Name: book_genres book_genres_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.book_genres
    ADD CONSTRAINT book_genres_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: books books_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.authors(id);


--
-- Name: stored_books stored_books_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.stored_books
    ADD CONSTRAINT stored_books_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id);


--
-- Name: stored_books stored_books_shelf_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yamen
--

ALTER TABLE ONLY public.stored_books
    ADD CONSTRAINT stored_books_shelf_id_fkey FOREIGN KEY (shelf_id) REFERENCES public.shelves(id);


--
-- PostgreSQL database dump complete
--


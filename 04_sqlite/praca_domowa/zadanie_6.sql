ALTER TABLE film
ADD COLUMN category_id int
REFERENCES category(category_id)
DEFAULT NULL;

UPDATE film 
SET category_id = (
	SELECT category_id FROM film_category WHERE film_id = film.film_id
);

DROP TABLE film_category;
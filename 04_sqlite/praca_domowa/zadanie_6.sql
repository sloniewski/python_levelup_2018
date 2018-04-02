ALTER TABLE film
ADD COLUMN category_id int
REFERENCES category(category_id)
DEFAULT NULL;

WITH a as (
	SELECT film_id, category_id
	FROM film_category
)
UPDATE film 
SET category_id = (
	SELECT category_id FROM a WHERE film_id = film.film_id
);
SELECT film.film_id, category.name from film 
JOIN film_category ON film_category.film_id = film.film_id
JOIN category ON category.category_id = film_category.category_id;
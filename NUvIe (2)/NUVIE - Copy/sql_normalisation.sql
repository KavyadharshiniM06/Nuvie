use hemni;

select * from Movies;
select *  from movies_nf where title like '20062007';
CREATE TABLE movies_nf (
    movie_id INT PRIMARY KEY,
    title VARCHAR(255)
);
CREATE TABLE genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE
);

CREATE TABLE movie_genres (
    movie_id INT,
    genre_id INT,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id),
    PRIMARY KEY (movie_id, genre_id)
);

CREATE TEMPORARY TABLE split_genres (
    genre VARCHAR(50)
);

-- Manually extract and insert unique genres
INSERT IGNORE INTO split_genres (genre)
SELECT DISTINCT SUBSTRING_INDEX(SUBSTRING_INDEX(genres, '|', n.n), '|', -1) AS genre
FROM movies
JOIN (
    SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
    UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
) n ON CHAR_LENGTH(genres) - CHAR_LENGTH(REPLACE(genres, '|', '')) >= n.n - 1;

-- Insert distinct genres into the genres table
INSERT IGNORE INTO genres (genre_name)
SELECT DISTINCT genre FROM split_genres WHERE genre IS NOT NULL;

-- Join and insert movie_id + genre_id pairs
INSERT INTO movie_genres (movie_id, genre_id)
SELECT DISTINCT
    m.movie_id,
    g.genre_id
FROM movies m
JOIN (
    SELECT 
        movie_id,
        SUBSTRING_INDEX(SUBSTRING_INDEX(genres, '|', n.n), '|', -1) AS genre
    FROM movies
    JOIN (
        SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
        UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
    ) n ON CHAR_LENGTH(genres) - CHAR_LENGTH(REPLACE(genres, '|', '')) >= n.n - 1
) mg ON mg.movie_id = m.movie_id
JOIN genres g ON mg.genre = g.genre_name;

ALTER TABLE movies_nf ADD COLUMN release_year INT;

UPDATE movies_nf
SET release_year = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(title, '(', -1), ')', 1) AS UNSIGNED)
WHERE title LIKE '%(%'AND
      title NOT LIKE '%–%';
CREATE TABLE years (
    year_id INT AUTO_INCREMENT PRIMARY KEY,
    release_year INT UNIQUE
);

INSERT INTO years (release_year)
SELECT DISTINCT release_year FROM movies_nf WHERE release_year IS NOT NULL;

ALTER TABLE movies_nf MODIFY COLUMN release_year VARCHAR(40);

ALTER TABLE movies_nf ADD COLUMN year_id INT;

UPDATE movies_nf m
JOIN years y ON m.release_year = y.release_year
SET m.year_id = y.year_id;

ALTER TABLE movies_nf DROP COLUMN release_year;


select * from movie_genres;
select * from movies_nf;
select * from years;
select * from genres;

SET SQL_SAFE_UPDATES = 0;

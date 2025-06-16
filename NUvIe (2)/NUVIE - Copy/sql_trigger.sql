use hemni;

CREATE TABLE user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    genres VARCHAR(255),
    rating FLOAT,
    year_range VARCHAR(20),
    tags VARCHAR(255),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    genres VARCHAR(255),
    rating FLOAT,
    year_range VARCHAR(20),
    tags VARCHAR(255),
    queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER //

CREATE TRIGGER log_user_query
AFTER INSERT ON user_preferences
FOR EACH ROW
BEGIN
    INSERT INTO user_queries (genres, rating, year_range, tags)
    VALUES (NEW.genres, NEW.rating, NEW.year_range, NEW.tags);
END //

DELIMITER ;

select * from user_queries;

select * from user_preferences;


const express = require('express');
const mysql = require('mysql2');
const multer = require('multer');
const bodyParser = require('body-parser');
const path = require('path');

// Setup Express app
const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('uploads')); // For serving profile images

// Create MySQL connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root', // Replace with your MySQL username
    password: 'tiger', // Replace with your MySQL password
    database: 'signupDB' // Your MySQL database name
});

db.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL:', err);
        return;
    }
    console.log('Connected to MySQL');
});

// Define multer storage configuration for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, './uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});
const upload = multer({ storage: storage });

// Create the `users` table if it doesn't exist
db.query(`
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(20),
        dob DATE,
        address VARCHAR(255),
        city VARCHAR(100),
        zipcode VARCHAR(20),
        profile_image VARCHAR(255)
    )
`, (err, result) => {
    if (err) console.log('Error creating table:', err);
});

// Signup route
app.post('/signup', upload.single('profile_image'), (req, res) => {
    const { username, password, email, phone, dob, address, city, zipcode } = req.body;
    const profileImage = req.file ? req.file.filename : null;

    // Insert data into MySQL
    const query = `
        INSERT INTO users (username, password, email, phone, dob, address, city, zipcode, profile_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    db.query(query, [username, password, email, phone, dob, address, city, zipcode, profileImage], (err, result) => {
        if (err) {
            console.log('Error inserting user:', err);
            res.send('Error in signup!');
        } else {
            res.send('User signed up successfully!');
        }
    });
});

// Start server
const port = 3302;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

const express = require('express');
const mysql = require('mysql');
const fs = require('fs');

const app = express();
const port = 1337;

let FLAG;
try {
    FLAG = fs.readFileSync('/flag.txt', 'utf-8').trim();
} catch (err) {
    console.error('Error reading flag file:', err);
    FLAG = null; // Handle missing or unreadable flag file
}

app.get('/flag', async (req, res) => {
    try {
        const connectionString = req.query.connectionString;

        if (!connectionString) {
            return res.status(400).send('Missing connectionString query parameter.');
        }

        const connection = mysql.createConnection(connectionString);

        connection.connect(err => {
            if (err) {
                console.error('Database connection error:', err);
                return res.status(500).send('Database connection failed.');
            }

            connection.query('SELECT content FROM FLAG', (err, results) => {
                connection.end();

                if (err) {
                    console.error('Query error:', err);
                    return res.status(404).send('Where is your flag?');
                }

                if (!results || results.length === 0) {
                    return res.status(404).send('Where is your flag?');
                }

                const yourFlag = results[0]?.content;

                if (FLAG && FLAG === yourFlag) {
                    return res.send('YES!');
                } else {
                    return res.send('NOP.');
                }
            });
        });
    } catch (error) {
        console.error('Unexpected error:', error);
        res.status(500).send('An unexpected error occurred.');
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});


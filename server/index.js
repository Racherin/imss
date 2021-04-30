// server/index.js

const express = require("express");
const path = require('path');

const PORT = process.env.PORT || 3001;

const app = express();


app.get("/",(req,res) => {
    res.sendFile(path.join(__dirname, '/index.html'));
})

app.listen(PORT, () => {
    console.log(`Server listening on ${PORT}`);
});
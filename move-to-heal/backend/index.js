const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();
const app = express();

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: 'Move To Heal Backend API Running' });
});

const authRoutes = require('./routes/auth');
const dietRoutes = require('./routes/diet');

app.use('/api/auth', authRoutes);
app.use('/api/diet', dietRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Node.js Backend Server started on port ${PORT}`);
});

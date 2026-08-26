const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'DMS Backend Running' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Backend live on port ${PORT}`));
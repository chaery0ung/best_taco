const path = require('path');
const express = require('express');
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

const app = express();

app.get('/api/welcome-user', async (req, res) => {
  try {
    const result = await pool.query('SELECT name FROM users ORDER BY id LIMIT 1');
    res.json({ name: result.rows[0]?.name ?? null });
  } catch (err) {
    console.error('Failed to fetch welcome user:', err.message);
    res.status(500).json({ name: null });
  }
});

app.use(express.static(path.join(__dirname)));

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`best_taco listening on port ${port}`));

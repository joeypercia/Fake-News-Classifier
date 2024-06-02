const express = require('express');
const cassandra = require('cassandra-driver');
const cors = require('cors');

const app = express();
app.use(cors());

const client = new cassandra.Client({
  contactPoints: ['localhost'],
  localDataCenter: 'datacenter1',
  keyspace: 'pred'
});

app.get('/predictions', async (req, res) => {
  try {
    const query = 'SELECT * FROM predictions LIMIT 20';
    const result = await client.execute(query);
    res.json(result.rows);
  } catch (err) {
    res.status(500).send(err);
  }
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

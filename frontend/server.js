const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/health', (req, res) => {
  res.json({ status: 'ok', app: 'devops-server-manager-ui' });
});

app.listen(PORT, () => {
  console.log(`UI đang chạy tại http://localhost:${PORT}`);
});

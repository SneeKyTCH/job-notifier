const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'app/public')));

// Serve index.html for root path
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'app/public/index.html'));
});

// Fallback to index.html for SPA routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'app/public/index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 JobNotify web server running at http://localhost:${PORT}`);
  console.log(`📱 Open your browser to see the landing page`);
});

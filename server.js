const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { spawn } = require('child_process');
const WebSocket = require('ws');
const node_ssh = require('node-ssh');
const app = express();
const ssh = new node_ssh();

const port = 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

const server = app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});


const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  console.log('Client connected');

  const shell = spawn('bash');

  shell.stdout.on('data', (data) => {
    ws.send(data.toString());
  });

  shell.stderr.on('data', (data) => {
    ws.send(`ERROR: ${data.toString()}`);
  });

  shell.on('close', (code) => {
    ws.send(`Shell exited with code ${code}`);
    ws.close();
  });

  ws.on('message', (message) => {
    ws.send(`> ${message}\n`);
    shell.stdin.write(`${message}\n`);
  });

  ws.on('close', () => {
    console.log('Client disconnected');
    shell.kill();
  });
});

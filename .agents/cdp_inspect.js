const http = require('http');
const fs = require('fs');

async function getWsUrl() {
  return new Promise((resolve, reject) => {
    http.get('http://localhost:9222/json', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const list = JSON.parse(data);
        const page = list.find(p => p.type === 'page');
        if (page && page.webSocketDebuggerUrl) {
          resolve(page.webSocketDebuggerUrl);
        } else {
          reject(new Error('No page found'));
        }
      });
    }).on('error', reject);
  });
}

async function evalCdp(expression) {
  const wsUrl = await getWsUrl();
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => {
      ws.send(JSON.stringify({
        id: 1,
        method: 'Runtime.evaluate',
        params: {
          expression: expression,
          returnByValue: true
        }
      }));
    };
    ws.onmessage = (msg) => {
      const data = JSON.parse(msg.data);
      ws.close();
      if (data.result && data.result.result) {
        resolve(data.result.result.value);
      } else {
        resolve(data);
      }
    };
    ws.onerror = reject;
  });
}

async function main() {
  let expr = process.argv[2] || 'location.href';
  if (expr.endsWith('.js') && fs.existsSync(expr)) {
    expr = fs.readFileSync(expr, 'utf8');
  }
  const res = await evalCdp(expr);
  console.log(typeof res === 'object' ? JSON.stringify(res, null, 2) : res);
}

main().catch(console.error);

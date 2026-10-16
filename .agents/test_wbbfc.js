const http = require('http');

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

const code = `(() => {
  const scrollPane = document.querySelector('yt-scroll-pane');
  if (!scrollPane) return 'no scrollPane';
  const origBox = scrollPane.querySelector('.WBbfC');
  if (!origBox) return 'no origBox';

  let customBox = document.getElementById('yt-ac-update-detail-wbbfc');
  if (!customBox) {
    customBox = document.createElement('div');
    customBox.id = 'yt-ac-update-detail-wbbfc';
    customBox.className = 'WBbfC';
    customBox.style.paddingTop = '0rem';
    customBox.style.paddingRight = '1.84rem';
    customBox.innerHTML = 
      '<div class="XMA1jc"><div class="vjkzh">업데이트 검사</div><div class="LNwekb">선택(확인) 시 최신 릴리스 즉시 확인</div></div>' +
      '<div class="XMA1jc"><div class="vjkzh">배포 방식</div><div class="LNwekb">GitHub OTA 원클릭 업데이트</div></div>' +
      '<div class="XMA1jc"><div class="vjkzh">기능 상태</div><div class="LNwekb">Zero-Ad 광고 차단 및 4K 지원 활성화</div></div>';
    origBox.parentElement.appendChild(customBox);
  }
  origBox.style.display = 'none';
  customBox.style.display = 'block';
  return 'Success WBbfC injected';
})()`;

evalCdp(code).then(console.log).catch(console.error);

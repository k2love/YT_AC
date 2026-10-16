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
  const container = document.querySelector('ytlr-tv-surface-content-renderer');
  if (!container) return 'no container';
  const item = container.querySelector('ytlr-setting-read-only-item-renderer');
  if (item) item.style.display = 'none';

  let view = document.getElementById('yt-ac-update-detail-view');
  if (!view) {
    view = document.createElement('div');
    view.id = 'yt-ac-update-detail-view';
    view.style.cssText = 'padding: 40px 60px; color: #fff; font-family: Roboto, sans-serif;';
    view.innerHTML = '<h2 style="font-size: 2.2rem; font-weight: 500; margin-bottom: 20px; color: #fff;">최신 앱 업데이트 확인</h2>' +
      '<p style="font-size: 1.3rem; color: #aaa; line-height: 1.6; margin-bottom: 30px;">리모컨의 <b>[확인 / 선택]</b> 버튼을 누르면 최신 버전 업데이트를 즉시 검사합니다.<br>새 버전이 감지되면 간편하게 바로 업데이트할 수 있습니다.</p>' +
      '<div style="background: rgba(255,255,255,0.08); border-radius: 12px; padding: 24px 28px; max-width: 650px;">' +
      '<div style="font-size: 1.2rem; color: #fff; margin-bottom: 12px; font-weight: 500;">주요 기능</div>' +
      '<div style="font-size: 1.1rem; color: #bbb; margin-bottom: 8px;">✔ 무광고 클린 재생 (Zero-Ad)</div>' +
      '<div style="font-size: 1.1rem; color: #bbb; margin-bottom: 8px;">✔ 4K UHD 화질 복원 엔진</div>' +
      '<div style="font-size: 1.1rem; color: #bbb;">✔ GitHub OTA 최신 앱 자동/수동 검사</div>' +
      '</div>';
    container.appendChild(view);
  }
  view.style.display = 'block';
  return 'Detail view shown';
})()`;

evalCdp(code).then(console.log).catch(console.error);

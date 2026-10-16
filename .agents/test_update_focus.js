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
  const myTab = document.getElementById('yt-ac-settings-update-banner');
  const allTabs = Array.from(document.querySelectorAll('ytlr-tab-renderer'));
  const versionTab = allTabs.find(t => t !== myTab && t.innerText.includes('앱 버전'));

  // 1. Unfocus versionTab
  if (versionTab) {
    versionTab.classList.remove('V0Tdtb', 'qzhmA', 'zylon-focus');
    versionTab.classList.add('JqwODe');
    const btn = versionTab.querySelector('ytlr-button');
    if (btn) {
      btn.classList.remove('BZ345e', 'zylon-focus');
      btn.classList.add('pAenK');
    }
  }

  // 2. Focus myTab
  if (myTab) {
    myTab.classList.add('V0Tdtb', 'qzhmA', 'zylon-focus');
    const btn = myTab.querySelector('ytlr-button');
    if (btn) {
      btn.classList.add('BZ345e', 'zylon-focus');
      btn.classList.remove('pAenK');
    }
  }

  // 3. Update right panel
  const updatePanelId = 'yt-ac-update-detail-view';
  let p = document.getElementById(updatePanelId);
  const versionView = document.querySelector('ytlr-setting-app-version');
  const parent = versionView ? versionView.parentElement : null;
  if (versionView) versionView.style.display = 'none';

  if (!p && parent) {
    p = document.createElement('div');
    p.id = updatePanelId;
    p.style.cssText = 'padding: 40px 60px; color: #fff; font-family: Roboto, sans-serif;';
    p.innerHTML = '<h2 style=\"font-size: 2.2rem; font-weight: 500; margin-bottom: 20px; color: #fff;\">최신 앱 업데이트 확인</h2>' +
      '<p style=\"font-size: 1.3rem; color: #aaa; line-height: 1.6; margin-bottom: 30px;\">리모컨의 <b>[확인 / 선택]</b> 버튼을 누르면 최신 버전 업데이트를 즉시 검사합니다.<br>새 버전이 감지되면 간편하게 바로 업데이트할 수 있습니다.</p>' +
      '<div style=\"background: rgba(255,255,255,0.08); border-radius: 12px; padding: 20px 24px; max-width: 600px;\">' +
      '<div style=\"font-size: 1.1rem; color: #fff; margin-bottom: 8px;\"><b>기능 안내</b></div>' +
      '<div style=\"font-size: 1.0rem; color: #888;\">• 무광고 클린 재생 (Zero-Ad)</div>' +
      '<div style=\"font-size: 1.0rem; color: #888; margin-top: 4px;\">• 4K UHD 화질 복원</div>' +
      '<div style=\"font-size: 1.0rem; color: #888; margin-top: 4px;\">• GitHub OTA 자동/수동 원클릭 업데이트</div>' +
      '</div>';
    parent.appendChild(p);
  }
  if (p) p.style.display = 'block';

  return 'Simulated focus on update tab';
})()`;

evalCdp(code).then(console.log).catch(console.error);

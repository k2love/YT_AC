(() => {
  const guideItems = Array.from(document.querySelectorAll('ytlr-guide-item-renderer, ytlr-guide-entry-renderer, [role="menuitem"], ytlr-pivot-bar-item-renderer, ytlr-button'));
  const settingsItem = guideItems.find(el => {
    const txt = (el.innerText || el.textContent || '').trim();
    const label = el.getAttribute('aria-label') || '';
    return txt.includes('설정') || label.includes('설정') || label.includes('Settings');
  });
  if (settingsItem) {
    const btn = settingsItem.querySelector('button, [role="button"], ytlr-button') || settingsItem;
    btn.click();
    return 'Clicked settings: ' + (settingsItem.innerText || settingsItem.getAttribute('aria-label'));
  }
  return 'Not found, items count: ' + guideItems.length;
})()

(() => {
  const el = document.activeElement;
  const tabs = Array.from(document.querySelectorAll('ytlr-tab-renderer'));
  return {
    activeElement: el ? (el.tagName + '.' + el.className + '#' + el.id) : null,
    activeText: el ? el.innerText.substring(0, 30) : null,
    tabsCount: tabs.length,
    tabs: tabs.map(t => ({
      text: t.innerText.trim(),
      display: t.style.display,
      classes: t.className
    }))
  };
})()

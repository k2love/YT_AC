(() => {
  const myTab = document.getElementById('yt-ac-settings-update-banner');
  if (!myTab) return 'No myTab';
  const group = myTab.parentElement;
  const grandParent = group.parentElement;
  return {
    grandParentTag: grandParent.tagName,
    grandParentClass: grandParent.className,
    groups: Array.from(grandParent.children).map(g => ({
      tag: g.tagName,
      className: g.className,
      items: Array.from(g.children).map(c => (c.innerText || '').trim())
    }))
  };
})()

(() => {
  const myTab = document.getElementById('yt-ac-settings-update-banner');
  if (!myTab) return 'No myTab';
  const parent = myTab.parentElement;
  return {
    parentTag: parent.tagName,
    parentClass: parent.className,
    parentId: parent.id,
    children: Array.from(parent.children).map(c => ({
      tag: c.tagName,
      id: c.id,
      text: (c.innerText || '').substring(0, 30)
    }))
  };
})()

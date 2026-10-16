(() => {
  const allTabs = Array.from(document.querySelectorAll('ytlr-tab-renderer'));
  const myTab = document.getElementById('yt-ac-settings-update-banner');
  const versionTab = allTabs.find(t => t !== myTab && t.innerText.includes('앱 버전'));
  const prevTab = myTab ? myTab.previousElementSibling : null;

  return {
    hasMyTab: !!myTab,
    myTabNext: myTab ? (myTab.nextElementSibling ? myTab.nextElementSibling.innerText.trim() : null) : null,
    myTabPrev: myTab ? (myTab.previousElementSibling ? myTab.previousElementSibling.innerText.trim() : null) : null,
    prevKeyAttached: prevTab ? prevTab._k2KeyAttached : null,
    versionKeyAttached: versionTab ? versionTab._k2KeyAttached : null
  };
})()

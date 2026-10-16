(() => {
  const tabs = Array.from(document.querySelectorAll('ytlr-tab-renderer'));
  const inst0 = tabs[0].__instance;
  const inst1 = tabs[1].__instance;
  function getMethods(obj) {
    if (!obj) return [];
    let p = obj;
    const names = [];
    while (p && p !== Object.prototype) {
      names.push(...Object.getOwnPropertyNames(p));
      p = Object.getPrototypeOf(p);
    }
    return names.filter(n => typeof obj[n] === 'function');
  }
  return {
    inst0Methods: getMethods(inst0).slice(0, 20),
    inst1Methods: getMethods(inst1).slice(0, 20),
    inst0Props: Object.keys(inst0 || {})
  };
})()

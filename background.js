chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get({ enabled: true }, (res) => {
    if (res.enabled === undefined) {
      chrome.storage.sync.set({ enabled: true });
    }
  });
});

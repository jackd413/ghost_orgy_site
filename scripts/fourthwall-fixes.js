(() => {
  const moneySelectors = [
    ".product-info__price",
    ".tile__price",
    ".inline-image__price",
    ".product-drawer__subtotal-value",
    ".product-drawer__subtotal-item--value"
  ].join(",");

  const normalizeMoneyText = (node) => {
    const before = node.textContent;
    if (!before) return;
    const after = before.replace(/(\$\s*\d[\d,]*)[,]([0-9]{2})(?!\d)/g, "$1.$2");
    if (after !== before) node.textContent = after;
  };

  const normalizePrices = (root = document) => {
    root.querySelectorAll(moneySelectors).forEach(normalizeMoneyText);
  };

  const markBrokenSocialMedia = (root = document) => {
    root.querySelectorAll(".instagram-feed__image, .video-tile__image img").forEach((img) => {
      if (img.dataset.goFallbackBound) return;
      img.dataset.goFallbackBound = "true";
      img.addEventListener("error", () => {
        const tile = img.closest(".instagram-feed__post, .video-tile__link, .video-tile__image");
        if (tile) tile.classList.add("go-media-failed");
      });
    });
  };

  const run = (root = document) => {
    normalizePrices(root);
    markBrokenSocialMedia(root);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => run());
  } else {
    run();
  }

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === Node.ELEMENT_NODE) run(node);
      });
      if (mutation.type === "characterData" && mutation.target.parentElement) {
        const parent = mutation.target.parentElement;
        if (parent.matches(moneySelectors)) normalizeMoneyText(parent);
      }
    }
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
    characterData: true
  });
})();

document.querySelectorAll("[data-current-year]").forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});

function trackEvent(name, params = {}) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ ...params, event: name });
}

document.querySelectorAll("a[data-track], button[data-track]").forEach((item) => {
  item.addEventListener("click", () => {
    trackEvent("click", {
      event_category: "engagement",
      event_label: item.dataset.track,
      destination: item.href || ""
    });
  });
});

document.querySelectorAll("[data-copy-target]").forEach((trigger) => {
  trigger.addEventListener("click", async (event) => {
    event.preventDefault();
    const target = document.getElementById(trigger.dataset.copyTarget);
    if (!target) return;
    target.select();
    target.setSelectionRange(0, target.value.length);
    try {
      await navigator.clipboard.writeText(target.value);
    } catch (error) {
      document.execCommand("copy");
    }
    trigger.textContent = trigger.dataset.copyLabel || "Copied";
    trackEvent("copy", {
      event_category: "engagement",
      event_label: trigger.dataset.copyTarget
    });
  });
});

document.querySelectorAll("[data-subscribe-form]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const input = form.querySelector('input[name="email"]');
    const status = form.parentElement.querySelector("[data-subscribe-status]");
    const email = input ? input.value.trim() : "";
    if (!email) return;
    const subject = encodeURIComponent("Subscribe to Ghost Orgy transmissions");
    const body = encodeURIComponent(`Please add ${email} to the Ghost Orgy update list.`);
    if (status) status.textContent = "Opening email request...";
    trackEvent("generate_lead", {
      event_category: "conversion",
      event_label: "updates_mailto_subscribe"
    });
    window.location.href = `mailto:info@unholyghost.org?subject=${subject}&body=${body}`;
  });
});

function toolHandleAnchorToggle(isChecked) {
    const event = new CustomEvent('tool-setting-changed', {
        detail: { type: "anchor", value: isChecked }
      });
    window.dispatchEvent(event);
}


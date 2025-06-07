document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form.popup-submit').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const msg = form.dataset.message || '送信中...';
      const popup = document.createElement('div');
      popup.className = 'popup';
      popup.textContent = msg;
      document.body.appendChild(popup);
      setTimeout(() => {
        form.submit();
      }, 500);
      setTimeout(() => {
        popup.remove();
      }, 1000);
    });
  });
});

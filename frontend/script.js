const healthStatus = document.querySelector('#healthStatus');
const form = document.querySelector('#contactForm');
const responseBox = document.querySelector('#responseBox');

async function checkHealth() {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    healthStatus.textContent = data.status === 'ok' ? 'онлайн' : 'неизвестно';
  } catch (error) {
    healthStatus.textContent = 'офлайн';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  responseBox.textContent = 'Отправка запроса...';

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch('/api/contact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    responseBox.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    responseBox.textContent = JSON.stringify({
      status: 'error',
      message: error.message,
    }, null, 2);
  }
});

checkHealth();
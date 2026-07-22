const healthStatus = document.querySelector('#healthStatus');
const statusDot = document.querySelector('#statusDot');
const totalRequests = document.querySelector('#totalRequests');
const aiSuccess = document.querySelector('#aiSuccess');
const form = document.querySelector('#contactForm');
const responseBox = document.querySelector('#responseBox');
const responseBadge = document.querySelector('#responseBadge');
const submitButton = document.querySelector('#submitButton');
const fillExampleButton = document.querySelector('#fillExample');

const examplePayload = {
  name: 'Иван Шевченко',
  phone: '+79780260009',
  email: 'test@example.com',
  comment: 'Здравствуйте! Хочу обсудить разработку backend API для лендинга с AI-анализом заявки и email-уведомлениями.',
};

async function checkHealth() {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    const isOnline = response.ok && data.status === 'ok';

    healthStatus.textContent = isOnline ? 'онлайн' : 'ошибка';
    statusDot.classList.toggle('status-dot--offline', !isOnline);
  } catch (error) {
    healthStatus.textContent = 'офлайн';
    statusDot.classList.add('status-dot--offline');
  }
}

async function loadMetrics() {
  try {
    const response = await fetch('/api/metrics');
    const data = await response.json();

    totalRequests.textContent = data.total_requests ?? 0;
    aiSuccess.textContent = data.ai_success ?? 0;
  } catch (error) {
    totalRequests.textContent = '—';
    aiSuccess.textContent = '—';
  }
}

function setResponseState(state, text) {
  responseBadge.textContent = text;
  responseBadge.className = `response-badge response-badge--${state}`;
}

fillExampleButton.addEventListener('click', () => {
  Object.entries(examplePayload).forEach(([key, value]) => {
    form.elements[key].value = value;
  });
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  responseBox.textContent = 'Отправка запроса...';
  setResponseState('loading', 'отправка');
  submitButton.disabled = true;
  submitButton.textContent = 'Отправляем...';

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
    setResponseState(response.ok ? 'success' : 'error', response.ok ? 'успешно' : `ошибка ${response.status}`);
    await loadMetrics();
  } catch (error) {
    responseBox.textContent = JSON.stringify({
      status: 'error',
      message: error.message,
    }, null, 2);
    setResponseState('error', 'ошибка');
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Отправить заявку';
  }
});

checkHealth();
loadMetrics();

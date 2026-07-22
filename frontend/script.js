const healthStatus = document.querySelector('#healthStatus');
const statusDot = document.querySelector('#statusDot');
const form = document.querySelector('#contactForm');
const responseBox = document.querySelector('#responseBox');
const responseStatus = document.querySelector('#responseStatus');
const fillExampleButton = document.querySelector('#fillExample');

const exampleData = {
  name: 'Иван Шевченко',
  phone: '+79780260009',
  email: 'shevchenko.i.i.2.22@gmail.com',
  comment: 'Здравствуйте! Хочу обсудить разработку backend API для лендинга с AI-анализом заявки и email-уведомлениями.',
};

function setBadge(type, text) {
  responseStatus.className = 'badge';

  if (type) {
    responseStatus.classList.add(type);
  }

  responseStatus.textContent = text;
}

function setHealth(status) {
  healthStatus.textContent = status;
  statusDot.className = 'status__dot';

  if (status === 'онлайн') {
    statusDot.classList.add('online');
  }

  if (status === 'офлайн') {
    statusDot.classList.add('offline');
  }
}

async function fetchWithTimeout(url, options = {}, timeout = 45000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    return response;
  } finally {
    clearTimeout(timer);
  }
}

async function checkHealth() {
  try {
    const response = await fetchWithTimeout('/api/health', {}, 10000);
    const data = await response.json();

    setHealth(data.status === 'ok' ? 'онлайн' : 'неизвестно');
  } catch (error) {
    setHealth('офлайн');
  }
}

fillExampleButton.addEventListener('click', () => {
  Object.entries(exampleData).forEach(([key, value]) => {
    const field = form.elements[key];

    if (field) {
      field.value = value;
    }
  });
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  setBadge('', 'отправка');
  responseBox.textContent = 'Отправка запроса...';

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetchWithTimeout('/api/contact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    }, 60000);

    const data = await response.json();

    responseBox.textContent = JSON.stringify(data, null, 2);

    if (response.ok) {
      setBadge('success', 'успешно');
    } else {
      setBadge('error', `ошибка ${response.status}`);
    }
  } catch (error) {
    const message = error.name === 'AbortError'
      ? 'Запрос выполнялся слишком долго и был остановлен. Проверьте работу контейнера и внешних сервисов.'
      : error.message;

    setBadge('error', 'ошибка');

    responseBox.textContent = JSON.stringify(
      {
        status: 'error',
        message,
      },
      null,
      2,
    );
  }
});

checkHealth();

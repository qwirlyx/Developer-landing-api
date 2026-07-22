const healthStatus = document.querySelector('#healthStatus');
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

async function checkHealth() {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();

    healthStatus.textContent = data.status === 'ok' ? 'онлайн' : 'неизвестно';
  } catch (error) {
    healthStatus.textContent = 'офлайн';
  }
}

function setResponseStatus(type, text) {
  responseStatus.className = 'response-status';

  if (type) {
    responseStatus.classList.add(type);
  }

  responseStatus.textContent = text;
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

  setResponseStatus('', 'отправка');
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

    if (response.ok) {
      setResponseStatus('success', 'успешно');
    } else {
      setResponseStatus('error', `ошибка ${response.status}`);
    }
  } catch (error) {
    setResponseStatus('error', 'ошибка');

    responseBox.textContent = JSON.stringify(
      {
        status: 'error',
        message: error.message,
      },
      null,
      2,
    );
  }
});

checkHealth();

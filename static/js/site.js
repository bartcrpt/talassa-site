document.addEventListener('DOMContentLoaded', () => {
  initSiteNav();
  initSiteUserMenu();
  initSiteAuth();
  initPhilosophyToggle();
  initSiteLightbox();
  initRoomGallery();
});

function initSiteNav() {
  const navToggle = document.querySelector('[data-site-nav-toggle]');
  const nav = document.querySelector('[data-site-nav]');

  if (!navToggle || !nav) {
    return;
  }

  navToggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    document.body.classList.toggle('site-nav-open', isOpen);
  });

  nav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      nav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('site-nav-open');
    });
  });
}

function initPhilosophyToggle() {
  const philosophyRoot = document.querySelector('[data-philosophy]');
  if (!philosophyRoot) {
    return;
  }

  const more = philosophyRoot.querySelector('[data-philosophy-more]');
  const expand = philosophyRoot.querySelector('[data-philosophy-expand]');
  const collapse = philosophyRoot.querySelector('[data-philosophy-collapse]');

  if (!more || !expand || !collapse) {
    return;
  }

  expand.addEventListener('click', () => {
    more.hidden = false;
    collapse.hidden = false;
    expand.hidden = true;
  });

  collapse.addEventListener('click', () => {
    more.hidden = true;
    collapse.hidden = true;
    expand.hidden = false;
  });
}

function initSiteLightbox() {
  const root = document.querySelector('[data-site-lightbox]');
  if (!root) {
    return;
  }

  const image = root.querySelector('[data-site-lightbox-image]');
  const counter = root.querySelector('[data-site-lightbox-counter]');
  const closeButton = root.querySelector('[data-site-lightbox-close]');
  const prevButton = root.querySelector('[data-site-lightbox-prev]');
  const nextButton = root.querySelector('[data-site-lightbox-next]');

  if (!image || !counter || !closeButton || !prevButton || !nextButton) {
    return;
  }

  const galleryMap = new Map();
  let currentSource = null;
  let currentIndex = 0;

  document.querySelectorAll('[data-lightbox-gallery-id]').forEach((node) => {
    const galleryId = node.getAttribute('data-lightbox-gallery-id');
    const itemsRaw = node.getAttribute('data-lightbox-items');
    if (!galleryId || !itemsRaw) {
      return;
    }

    try {
      galleryMap.set(galleryId, JSON.parse(itemsRaw));
    } catch (error) {
      console.error('Failed to parse lightbox items for', galleryId, error);
    }
  });

  const render = () => {
    const items = galleryMap.get(currentSource) || [];
    const currentItem = items[currentIndex];
    if (!currentItem) {
      return;
    }

    image.src = currentItem.src || currentItem.url || '';
    image.alt = currentItem.alt || '';
    counter.textContent = `${currentIndex + 1} / ${items.length}`;
  };

  const open = (source, index) => {
    if (!galleryMap.has(source)) {
      return;
    }

    currentSource = source;
    currentIndex = index;
    render();
    root.hidden = false;
    document.body.classList.add('site-lightbox-open');
  };

  const close = () => {
    root.hidden = true;
    document.body.classList.remove('site-lightbox-open');
  };

  const move = (direction) => {
    const items = galleryMap.get(currentSource) || [];
    if (!items.length) {
      return;
    }

    currentIndex = (currentIndex + direction + items.length) % items.length;
    render();
  };

  document.querySelectorAll('[data-lightbox-trigger]').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const source = trigger.getAttribute('data-lightbox-source');
      const index = Number(trigger.getAttribute('data-lightbox-index') || 0);
      if (!source) {
        return;
      }
      open(source, index);
    });
  });

  closeButton.addEventListener('click', close);
  prevButton.addEventListener('click', () => move(-1));
  nextButton.addEventListener('click', () => move(1));
  root.addEventListener('click', (event) => {
    if (event.target === root) {
      close();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (root.hidden) {
      return;
    }

    if (event.key === 'Escape') {
      close();
    } else if (event.key === 'ArrowLeft') {
      move(-1);
    } else if (event.key === 'ArrowRight') {
      move(1);
    }
  });
}

function initRoomGallery() {
  document.querySelectorAll('[data-room-gallery]').forEach((gallery) => {
    const itemsRaw = gallery.getAttribute('data-lightbox-items');
    const mainImage = gallery.querySelector('[data-room-gallery-main-image]');
    const counter = gallery.querySelector('[data-room-gallery-counter]');
    const mainTrigger = gallery.querySelector('[data-room-gallery-main]');
    const thumbs = Array.from(gallery.querySelectorAll('[data-room-gallery-thumb]'));

    if (!itemsRaw || !mainImage || !counter || !mainTrigger || !thumbs.length) {
      return;
    }

    let items = [];
    try {
      items = JSON.parse(itemsRaw);
    } catch (error) {
      console.error('Failed to parse room gallery items', error);
      return;
    }

    const setActive = (index) => {
      const item = items[index];
      if (!item) {
        return;
      }

      mainImage.src = item.src || item.url || '';
      mainImage.alt = item.alt || '';
      counter.textContent = `${index + 1} / ${items.length}`;
      mainTrigger.setAttribute('data-lightbox-index', String(index));
      thumbs.forEach((thumb, thumbIndex) => {
        thumb.classList.toggle('is-active', thumbIndex === index);
      });
    };

    thumbs.forEach((thumb) => {
      thumb.addEventListener('click', () => {
        const index = Number(thumb.getAttribute('data-index') || 0);
        setActive(index);
      });
    });
  });
}

function initSiteUserMenu() {
  const root = document.querySelector('[data-site-user-menu]');
  if (!root) {
    return;
  }

  const toggle = root.querySelector('[data-site-user-toggle]');
  const dropdown = root.querySelector('[data-site-user-dropdown]');

  if (!toggle || !dropdown) {
    return;
  }

  const close = () => {
    dropdown.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
  };

  toggle.addEventListener('click', (event) => {
    event.preventDefault();
    const isOpen = dropdown.hidden;
    dropdown.hidden = !isOpen;
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  document.addEventListener('click', (event) => {
    if (!root.contains(event.target)) {
      close();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      close();
    }
  });
}

function initSiteAuth() {
  const modal = document.querySelector('[data-site-auth-modal]');
  if (!modal) {
    return;
  }

  const body = document.body;
  const dialog = modal.querySelector('.site-auth-modal__dialog');
  const closeButtons = modal.querySelectorAll('[data-site-auth-close]');
  const openButtons = document.querySelectorAll('[data-site-auth-open]');
  const title = modal.querySelector('[data-site-auth-title]');
  const subtitle = modal.querySelector('[data-site-auth-subtitle]');
  const switchBox = modal.querySelector('[data-site-auth-switch]');
  const errorBox = modal.querySelector('[data-site-auth-error]');
  const defaultNextPage = modal.getAttribute('data-next') || window.location.pathname;
  const forms = {
    login: modal.querySelector('[data-site-auth-form="login"]'),
    register: modal.querySelector('[data-site-auth-form="register"]'),
    code: modal.querySelector('[data-site-auth-form="code"]'),
  };
  const phoneInputs = {
    login: modal.querySelector('[data-site-auth-phone="login"]'),
    register: modal.querySelector('[data-site-auth-phone="register"]'),
  };
  const phoneDisplay = modal.querySelector('[data-site-auth-phone-display]');
  const agreementInput = modal.querySelector('[data-site-auth-agreement]');
  const policyInput = modal.querySelector('[data-site-auth-policy]');
  const docModal = document.querySelector('[data-site-doc-modal]');
  const docTitle = docModal?.querySelector('[data-site-doc-title]');
  const docEyebrow = docModal?.querySelector('[data-site-doc-eyebrow]');
  const docContent = docModal?.querySelector('[data-site-doc-content]');
  const codeInputs = Array.from(modal.querySelectorAll('[data-site-auth-code-input]'));
  const backButton = modal.querySelector('[data-site-auth-back]');
  const resendButton = modal.querySelector('[data-site-auth-resend]');
  const submitButtons = modal.querySelectorAll('[data-site-auth-submit]');

  if (!dialog || !title || !subtitle || !switchBox || !errorBox || !forms.login || !forms.register || !forms.code) {
    return;
  }

  const state = {
    view: 'login',
    codeSource: 'login',
    phone: '',
    phoneDisplay: '',
    loading: false,
    nextPage: defaultNextPage,
  };

  const viewConfig = {
    login: {
      title: 'Вход в систему',
      subtitle: 'Введите номер телефона для получения SMS-кода',
      switchHtml: '<span>Нет аккаунта?</span><button type="button" data-site-auth-switch-view="register">Зарегистрируйтесь здесь</button>',
    },
    register: {
      title: 'Создать аккаунт',
      subtitle: 'Введите номер телефона для регистрации',
      switchHtml: '<span>Уже есть аккаунт?</span><button type="button" data-site-auth-switch-view="login">Войдите здесь</button>',
    },
    code: {
      title: 'Подтверждение входа',
      subtitle: 'Введите 6-значный SMS-код, отправленный на ваш номер',
      switchHtml: '<span>Не получили сообщение?</span><button type="button" data-site-auth-resend-link>Отправить код повторно</button>',
    },
  };

  const formatPhoneDisplay = (value) => {
    const digits = value.replace(/\D/g, '');
    if (!digits.length) return '';
    const source = digits.startsWith('7') ? digits.slice(1) : digits.startsWith('8') ? digits.slice(1) : digits;
    let result = '+7';
    if (source.length > 0) result += ' (' + source.slice(0, 3);
    if (source.length >= 3) result += ') ';
    if (source.length > 3) result += source.slice(3, 6);
    if (source.length > 6) result += '-' + source.slice(6, 8);
    if (source.length > 8) result += '-' + source.slice(8, 10);
    return result;
  };

  const extractDigits = (value) => {
    const digits = value.replace(/\D/g, '');
    if (digits.startsWith('7') || digits.startsWith('8')) {
      return digits.slice(1, 11);
    }
    return digits.slice(0, 10);
  };

  const isPhoneValid = (value) => extractDigits(value).length === 10;

  const setLoading = (loading) => {
    state.loading = loading;
    submitButtons.forEach((button) => {
      button.disabled = loading;
    });
    if (resendButton) {
      resendButton.disabled = loading;
    }
  };

  const setError = (message = '') => {
    errorBox.textContent = message;
    errorBox.hidden = !message;
  };

  const closeModal = () => {
    modal.hidden = true;
    body.classList.remove('site-auth-open');
    setError('');
  };

  const updateSwitchActions = () => {
    switchBox.innerHTML = viewConfig[state.view].switchHtml;

    switchBox.querySelectorAll('[data-site-auth-switch-view]').forEach((button) => {
      button.addEventListener('click', () => {
        const target = button.getAttribute('data-site-auth-switch-view');
        if (target) {
          switchView(target);
        }
      });
    });

    const resendLink = switchBox.querySelector('[data-site-auth-resend-link]');
    if (resendLink) {
      resendLink.addEventListener('click', () => {
        resendCode();
      });
    }
  };

  const switchView = (view) => {
    state.view = view;
    title.textContent = viewConfig[view].title;
    subtitle.textContent = viewConfig[view].subtitle;
    Object.entries(forms).forEach(([key, form]) => {
      form.hidden = key !== view;
    });
    updateSwitchActions();
    setError('');

    if (view === 'code') {
      phoneDisplay.textContent = state.phoneDisplay;
      codeInputs.forEach((input) => {
        input.value = '';
      });
      setTimeout(() => {
        codeInputs[0]?.focus();
      }, 80);
    }
  };

  const openModal = (view = 'login', nextPage = defaultNextPage) => {
    state.codeSource = view === 'register' ? 'register' : 'login';
    state.nextPage = nextPage || defaultNextPage;
    if (view === 'login' || view === 'register') {
      state.phone = '';
      state.phoneDisplay = '';
      if (phoneInputs.login) phoneInputs.login.value = '';
      if (phoneInputs.register) phoneInputs.register.value = '';
      if (agreementInput) agreementInput.checked = false;
      if (policyInput) policyInput.checked = false;
    }
    switchView(view);
    modal.hidden = false;
    body.classList.add('site-auth-open');
  };

  const requestJson = async (url, payload) => {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(payload),
    });

    let data = {};
    try {
      data = await response.json();
    } catch (error) {
      data = {};
    }

    if (!response.ok || data.success === false) {
      throw new Error(data.message || 'Не удалось выполнить запрос');
    }

    return data;
  };

  const sendCode = async (mode) => {
    const input = phoneInputs[mode];
    if (!input) {
      return;
    }

    const rawPhone = input.value || '';
    if (!isPhoneValid(rawPhone)) {
      setError('Введите корректный российский номер телефона');
      input.focus();
      return;
    }

    if (mode === 'register' && ((!agreementInput || !agreementInput.checked) || (!policyInput || !policyInput.checked))) {
      setError('Необходимо принять документы и согласие на обработку персональных данных');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const endpoint = mode === 'register' ? '/auth/api/register' : '/auth/api/login';
      const data = await requestJson(endpoint, {
        phone: '+7' + extractDigits(rawPhone),
        accepted_user_agreement: mode === 'register' ? Boolean(agreementInput && agreementInput.checked) : undefined,
        accepted_personal_data_policy: mode === 'register' ? Boolean(policyInput && policyInput.checked) : undefined,
      });

      state.codeSource = mode;
      state.phone = data.phone;
      state.phoneDisplay = data.phone_display || formatPhoneDisplay(data.phone || rawPhone);
      switchView('code');
    } catch (error) {
      setError(error.message || 'Не удалось отправить код');
    } finally {
      setLoading(false);
    }
  };

  const verifyCode = async () => {
    const code = codeInputs.map((input) => input.value).join('');
    if (code.length !== 6) {
      setError('Введите SMS-код полностью');
      codeInputs[0]?.focus();
      return;
    }

    try {
      setLoading(true);
      setError('');
      const data = await requestJson('/auth/api/verify', {
        phone: state.phone,
        sms_code: code,
        next: state.nextPage,
      });

      window.location.href = data.redirect_url || window.location.href;
    } catch (error) {
      setError(error.message || 'Неверный SMS-код');
    } finally {
      setLoading(false);
    }
  };

  const resendCode = async () => {
    if (!state.codeSource) {
      return;
    }

    const proxyValue = state.phoneDisplay || formatPhoneDisplay(state.phone);
    if (phoneInputs[state.codeSource]) {
      phoneInputs[state.codeSource].value = proxyValue;
    }
    await sendCode(state.codeSource);
  };

  const docs = {
    agreement: {
      eyebrow: 'Документ',
      title: 'Пользовательское соглашение и Правила использования сайта',
      content: `
        <p>Используя сайт «Таласса Hotel & Spa», вы подтверждаете, что используете его добросовестно и только для получения информации об отеле, выбора номера, отправки заявок и оформления бронирования.</p>
        <p>Пользователь обязуется указывать достоверные данные при регистрации и бронировании, не предпринимать действий, нарушающих работу сайта, и не использовать сайт для размещения ложных заявок или недобросовестных обращений.</p>
        <p>Администрация сайта вправе обновлять информацию о номерах, стоимости, услугах и правилах проживания без отдельного уведомления. Итоговые условия бронирования считаются подтверждёнными после связи с администратором и подтверждения заявки.</p>
        <p>Все материалы сайта, включая тексты, фотографии, дизайн и элементы интерфейса, используются только в информационных целях и не подлежат копированию или распространению без согласия правообладателя.</p>
      `,
    },
    policy: {
      eyebrow: 'Документ',
      title: 'Политика обработки персональных данных',
      content: `
        <p>Оставляя свои данные на сайте, вы соглашаетесь на их обработку для связи с вами, подтверждения регистрации, оформления бронирования, уточнения деталей проживания и направления сервисных уведомлений, связанных с вашей заявкой.</p>
        <p>К персональным данным могут относиться номер телефона, имя, адрес электронной почты и иные сведения, которые вы добровольно указываете при регистрации или бронировании.</p>
        <p>Данные используются только для работы отеля и не передаются третьим лицам без законных оснований. Администрация принимает разумные меры для защиты полученной информации от утраты, неправомерного доступа и раскрытия.</p>
        <p>Пользователь вправе запросить уточнение, обновление или удаление своих персональных данных, обратившись в отель по официальным контактам, указанным на сайте.</p>
      `,
    },
  };

  const openDocModal = (key) => {
    if (!docModal || !docTitle || !docContent || !docs[key]) {
      return;
    }
    docEyebrow.textContent = docs[key].eyebrow;
    docTitle.textContent = docs[key].title;
    docContent.innerHTML = docs[key].content;
    docModal.hidden = false;
    body.classList.add('site-doc-open');
  };

  const closeDocModal = () => {
    if (!docModal) {
      return;
    }
    docModal.hidden = true;
    body.classList.remove('site-doc-open');
  };

  modal.querySelectorAll('[data-site-auth-doc-open]').forEach((button) => {
    button.addEventListener('click', () => {
      const key = button.getAttribute('data-site-auth-doc-open');
      if (key) {
        openDocModal(key);
      }
    });
  });

  docModal?.querySelectorAll('[data-site-doc-close]').forEach((button) => {
    button.addEventListener('click', closeDocModal);
  });
  openButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const view = button.getAttribute('data-auth-view') || 'login';
      const nav = document.querySelector('[data-site-nav]');
      const navToggle = document.querySelector('[data-site-nav-toggle]');
      if (nav && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        navToggle?.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('site-nav-open');
      }
      const next = button.getAttribute('data-auth-next') || defaultNextPage;
      openModal(view, next);
    });
  });

  closeButtons.forEach((button) => {
    button.addEventListener('click', closeModal);
  });

  modal.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && docModal && !docModal.hidden) {
      closeDocModal();
      return;
    }
    if (modal.hidden) {
      return;
    }
    if (event.key === 'Escape') {
      closeModal();
    }
  });

  backButton?.addEventListener('click', () => {
    switchView(state.codeSource || 'login');
  });

  forms.login.addEventListener('submit', (event) => {
    event.preventDefault();
    sendCode('login');
  });

  forms.register.addEventListener('submit', (event) => {
    event.preventDefault();
    sendCode('register');
  });

  forms.code.addEventListener('submit', (event) => {
    event.preventDefault();
    verifyCode();
  });

  resendButton?.addEventListener('click', () => {
    resendCode();
  });

  Object.entries(phoneInputs).forEach(([mode, input]) => {
    input?.addEventListener('input', (event) => {
      const value = event.target.value;
      event.target.value = formatPhoneDisplay(value);
      if (state.view === mode) {
        setError('');
      }
    });
  });

  codeInputs.forEach((input, index) => {
    input.addEventListener('input', (event) => {
      const value = event.target.value.replace(/\D/g, '').slice(-1);
      event.target.value = value;
      setError('');
      if (value && index < codeInputs.length - 1) {
        codeInputs[index + 1].focus();
      }
      if (codeInputs.every((node) => node.value.length === 1)) {
        verifyCode();
      }
    });

    input.addEventListener('keydown', (event) => {
      if (event.key === 'Backspace' && !input.value && index > 0) {
        codeInputs[index - 1].focus();
      }
    });

    input.addEventListener('paste', (event) => {
      event.preventDefault();
      const digits = (event.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '').slice(0, 6);
      digits.split('').forEach((digit, digitIndex) => {
        if (codeInputs[digitIndex]) {
          codeInputs[digitIndex].value = digit;
        }
      });
      const nextIndex = Math.min(digits.length, codeInputs.length - 1);
      codeInputs[nextIndex]?.focus();
      if (digits.length === 6) {
        verifyCode();
      }
    });
  });

  updateSwitchActions();
}






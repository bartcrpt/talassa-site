document.addEventListener('DOMContentLoaded', () => {
  initSiteNav();
  initPhilosophyToggle();
  initRoomsFilter();
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

function initRoomsFilter() {
  const root = document.querySelector('[data-rooms-filter]');
  if (!root) {
    return;
  }

  const cards = Array.from(root.querySelectorAll('[data-room-card]'));
  const grid = root.querySelector('[data-rooms-grid]');
  const count = root.querySelector('[data-visible-count]');
  const categoryButtons = Array.from(root.querySelectorAll('[data-room-category]'));
  const sortButtons = Array.from(root.querySelectorAll('[data-room-sort]'));

  let activeCategory = root.getAttribute('data-initial-category') || 'Все';
  let sortBy = 'price';

  const render = () => {
    const filtered = cards.filter((card) => {
      if (activeCategory === 'Все') {
        return true;
      }
      return card.getAttribute('data-category') === activeCategory;
    });

    filtered.sort((a, b) => {
      const aValue = Number(a.getAttribute(`data-${sortBy}`) || 0);
      const bValue = Number(b.getAttribute(`data-${sortBy}`) || 0);
      return sortBy === 'area' ? bValue - aValue : aValue - bValue;
    });

    cards.forEach((card) => {
      card.hidden = true;
    });

    filtered.forEach((card) => {
      card.hidden = false;
      grid.appendChild(card);
    });

    if (count) {
      count.textContent = String(filtered.length);
    }
  };

  categoryButtons.forEach((button) => {
    button.addEventListener('click', () => {
      activeCategory = button.getAttribute('data-room-category') || 'Все';
      categoryButtons.forEach((item) => item.classList.toggle('is-active', item === button));
      render();
    });
  });

  sortButtons.forEach((button) => {
    button.addEventListener('click', () => {
      sortBy = button.getAttribute('data-room-sort') || 'price';
      sortButtons.forEach((item) => item.classList.toggle('is-active', item === button));
      render();
    });
  });

  const activeCategoryButton = categoryButtons.find((button) => button.getAttribute('data-room-category') === activeCategory);
  if (!activeCategoryButton && categoryButtons[0]) {
    categoryButtons[0].classList.add('is-active');
    activeCategory = categoryButtons[0].getAttribute('data-room-category') || 'Все';
  }

  render();
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

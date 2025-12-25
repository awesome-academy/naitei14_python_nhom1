const API_TIMEOUT_MS = 3000;
const ANIMATION_DURATION_MS = 300;
const FADE_DURATION_MS = 150;

const translations = {
  error: "{% trans 'An error occurred' %}",
  connectionError: "{% trans 'Connection error. Please try again' %}",
  removeFromFavorite: "{% trans 'Remove from favorites' %}",
  addToFavorite: "{% trans 'Add to favorites' %}",
  removedFromFavorite: "{% trans 'Removed from favorites' %}",
};

class FavoriteError extends Error {
  constructor(message) {
    super(message);
    this.name = "FavoriteError";
  }
}

function initializeFavorites(mode = "toggle") {
  if (mode === "toggle") {
    initializeToggleFavorite();
  } else if (mode === "remove") {
    initializeRemoveFavorite();
  }
}

function initializeToggleFavorite() {
  const favoriteForms = document.querySelectorAll(".favorite-form-badge");

  favoriteForms.forEach((form) => {
    form.addEventListener("submit", toggleFavoriteStatus);
  });
}

function toggleFavoriteStatus(e) {
  e.preventDefault();

  const form = this;
  const button = form.querySelector(".favorite-badge-btn");
  const icon = button.querySelector("i");
  const formData = new FormData(form);
  const url = form.action;

  button.classList.add("loading");
  button.disabled = true;

  fetch(url, {
    method: "POST",
    body: formData,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new FavoriteError(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        updateFavoriteButton(button, icon, data.is_favorited);

        showNotification(data.message, data.is_favorited ? "success" : "info");
      } else {
        showNotification("Có lỗi xảy ra", "error");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification(translations.connectionError, "error");
    })
    .finally(() => {
      button.classList.remove("loading");
      button.disabled = false;
    });
}

function updateFavoriteButton(button, icon, isFavorited) {
  if (isFavorited) {
    icon.classList.remove("far");
    icon.classList.add("fas");
    button.setAttribute("data-favorited", "true");
    button.setAttribute("title", translations.removeFromFavorite);
  } else {
    icon.classList.remove("fas");
    icon.classList.add("far");
    button.setAttribute("data-favorited", "false");
    button.setAttribute("title", translations.addToFavorite);
  }
}

function initializeRemoveFavorite() {
  const removeFavoriteForms = document.querySelectorAll(
    ".remove-favorite-form"
  );

  removeFavoriteForms.forEach((form) => {
    form.addEventListener("submit", removeFavoriteItem);
  });
}

function removeFavoriteItem(e) {
  e.preventDefault();

  const form = this;
  const button = form.querySelector(".favorite-btn-remove");
  const favoriteCard = form.closest(".favorite-card");
  const formData = new FormData(form);
  const url = form.action;

  button.classList.add("loading");
  button.disabled = true;

  fetch(url, {
    method: "POST",
    body: formData,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new FavoriteError(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      if (data.success && !data.is_favorited) {
        favoriteCard.classList.add("removing");

        setTimeout(() => {
          favoriteCard.remove();

          const container = document.getElementById("favorites-container");
          if (container && container.children.length === 0) {
            showNotification(translations.removedFromFavorite, "success");
            setTimeout(() => {
              location.reload();
            }, ANIMATION_DURATION_MS);
          } else {
            showNotification(data.message, "success");
          }
        }, ANIMATION_DURATION_MS);
      } else {
        showNotification("Có lỗi xảy ra", "error");
        button.classList.remove("loading");
        button.disabled = false;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification("Có lỗi kết nối. Vui lòng thử lại", "error");
      button.classList.remove("loading");
      button.disabled = false;
    });
}

function showNotification(message, type = "info") {
  let alertClass;
  let iconClass;

  switch (type) {
    case "success":
      alertClass = "alert-success";
      iconClass = "fa-check-circle";
      break;
    case "error":
      alertClass = "alert-danger";
      iconClass = "fa-exclamation-circle";
      break;
    case "info":
    default:
      alertClass = "alert-info";
      iconClass = "fa-info-circle";
  }

  const alertDiv = document.createElement("div");
  alertDiv.className = `alert ${alertClass} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
  alertDiv.setAttribute("role", "alert");
  alertDiv.style.zIndex = "9999";

  const contentDiv = document.createElement("div");
  contentDiv.className = "d-flex align-items-center";

  const iconSpan = document.createElement("i");
  iconSpan.className = `fas ${iconClass} me-2`;

  const messageSpan = document.createElement("span");
  messageSpan.textContent = message;

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "btn-close";
  closeBtn.setAttribute("data-bs-dismiss", "alert");
  closeBtn.setAttribute("aria-label", "Close");

  contentDiv.appendChild(iconSpan);
  contentDiv.appendChild(messageSpan);
  alertDiv.appendChild(contentDiv);
  alertDiv.appendChild(closeBtn);

  document.body.insertBefore(alertDiv, document.body.firstChild);

  setTimeout(() => {
    if (alertDiv) {
      alertDiv.classList.remove("show");
      setTimeout(() => {
        alertDiv.remove();
      }, FADE_DURATION_MS);
    }
  }, API_TIMEOUT_MS);
}

document.addEventListener("DOMContentLoaded", function () {
  const pitchesContainer = document.getElementById("pitches-container");
  if (pitchesContainer) {
    initializeFavorites("toggle");
  }
});

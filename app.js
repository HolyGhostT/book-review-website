
let books = [
  {id:1,title:"The Alchemist",author:"Paulo Coelho",genre:"Fiction",rating:4.8,color:"#d7c39d",ink:"#314331",symbol:"✳",desc:"A young shepherd follows a dream and discovers what it means to listen to his heart.",year:1988},
  {id:2,title:"Homegoing",author:"Yaa Gyasi",genre:"Fiction",rating:4.7,color:"#31513e",ink:"#f6e8c8",symbol:"✦",desc:"Two half-sisters and the generations that follow them across continents and time.",year:2016},
  {id:3,title:"The Creative Act",author:"Rick Rubin",genre:"Personal Growth",rating:4.6,color:"#c77751",ink:"#fff0d6",symbol:"☼",desc:"A thoughtful look at creativity, attention and making space for meaningful work.",year:2023},
  {id:4,title:"Atomic Habits",author:"James Clear",genre:"Personal Growth",rating:4.7,color:"#d7e0d1",ink:"#334734",symbol:"◉",desc:"Practical ideas for building better habits through small, consistent changes.",year:2018},
  {id:5,title:"Things Fall Apart",author:"Chinua Achebe",genre:"Classic",rating:4.9,color:"#b65f43",ink:"#fff0d6",symbol:"✺",desc:"A landmark novel exploring community, tradition and change in pre-colonial Nigeria.",year:1958},
  {id:6,title:"Pride and Prejudice",author:"Jane Austen",genre:"Classic",rating:4.5,color:"#e5c5b5",ink:"#5a3830",symbol:"❀",desc:"A sharp and witty story of first impressions, family expectations and love.",year:1813}
];

const starterReviews = [
  {id:"sample1",bookId:5,name:"Amara O.",rating:5,text:"Achebe makes the world of Umuofia feel real. I loved how the story shows both personal pride and the pressure of a changing society.",date:"Community pick"},
  {id:"sample2",bookId:1,name:"Michael K.",rating:5,text:"A simple story with a message that stays with you. It reminded me to pay attention to the journey, not only the destination.",date:"Community pick"},
  {id:"sample3",bookId:4,name:"Tomi S.",rating:4,text:"The practical examples made the ideas easy to understand. It is the kind of book I would revisit when trying to build a routine.",date:"Community pick"}
];

const coverPalette = [
  {bg:"#d7c39d",ink:"#314331"},
  {bg:"#31513e",ink:"#f6e8c8"},
  {bg:"#c77751",ink:"#fff0d6"},
  {bg:"#d7e0d1",ink:"#334734"},
  {bg:"#b65f43",ink:"#fff0d6"},
  {bg:"#e5c5b5",ink:"#5a3830"}
];

const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => [...root.querySelectorAll(selector)];

let activeGenre = "All";
let activeRating = 5;
let toastTimer;
let newsletterPopupTimer;

let databaseReviews = [];

function allReviews() {
  return [...databaseReviews, ...starterReviews];
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
}

function averageRating(bookId) {
  const reviews = allReviews().filter(r => Number(r.bookId) === bookId);

  if (!reviews.length) {
    return books.find(b => b.id === bookId).rating;
  }

  return reviews.reduce((sum, r) => sum + Number(r.rating), 0) / reviews.length;
}

function bookCover(book, index) {
  const palette = coverPalette[index % coverPalette.length];
  const title = book.title.replace(/:.*$/, "").split(" ");

  const display = title.length > 2
    ? `${title.slice(0, 2).join(" ")}<br>${title.slice(2).join(" ")}`
    : title.join("<br>");

  return `<div class="book-cover" style="background:${palette.bg}">
    <div class="cover-design" style="background:${palette.bg};color:${palette.ink}">
      <span class="cover-title">${display}</span>
      <span class="cover-author">${escapeHTML(book.author)}</span>
      <span class="cover-symbol">${book.symbol || "✳"}</span>
    </div>
  </div>`;
}

function renderBooks() {
  const query = $("#searchInput").value.trim().toLowerCase();

  const filtered = books.filter(b =>
    (activeGenre === "All" || b.genre === activeGenre) &&
    `${b.title} ${b.author} ${b.genre}`.toLowerCase().includes(query)
  );

  $("#bookCount").textContent = String(books.length).padStart(2, "0");

  $("#bookGrid").innerHTML = filtered.map(book => {
    const index = books.findIndex(b => b.id === book.id);

    return `<article class="book-card">
      ${bookCover(book, index)}
      <div class="book-card-meta">
        <span class="genre-tag">${escapeHTML(book.genre)}</span>
        <span class="book-rating"><span class="star">★</span>${averageRating(book.id).toFixed(1)}</span>
      </div>
      <h3>${escapeHTML(book.title)}</h3>
      <p class="book-author">by ${escapeHTML(book.author)}</p>
      <p class="book-desc">${escapeHTML(book.desc)}</p>
      <div class="card-actions">
        <button class="read-link" data-book="${book.id}">Read reviews ↗</button>
        <button data-write-book="${book.id}">Review this book +</button>
      </div>
    </article>`;
  }).join("");

  $("#emptyState").classList.toggle("hidden", filtered.length !== 0);

  $("#bookGrid").querySelectorAll("[data-book]").forEach(btn => {
    btn.addEventListener("click", () => showBookReviews(Number(btn.dataset.book)));
  });

  $("#bookGrid").querySelectorAll("[data-write-book]").forEach(btn => {
    btn.addEventListener("click", () => openReviewDialog(Number(btn.dataset.writeBook)));
  });
}

function renderReviews() {
  const reviews = allReviews().slice(0, 6);

  $("#reviewGrid").innerHTML = reviews.map(r => {
    const book = books.find(b => b.id === Number(r.bookId));

    if (!book) return "";

    const initials = r.name.split(/\s+/).map(s => s[0]).join("").slice(0, 2).toUpperCase();
    const date = r.date || "Just now";

    return `<article class="review-card">
      <div class="review-card-top">
        <span class="review-book">${escapeHTML(book.title)}</span>
        <span class="review-stars" aria-label="${r.rating} out of 5 stars">${"★".repeat(Number(r.rating))}${"☆".repeat(5 - Number(r.rating))}</span>
      </div>
      <blockquote>“${escapeHTML(r.text)}”</blockquote>
      <div class="review-author">
        <span class="review-avatar">${escapeHTML(initials)}</span>
        <span><strong>${escapeHTML(r.name)}</strong><small>${escapeHTML(date)}</small></span>
      </div>
    </article>`;
  }).join("");
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, c => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[c]));
}

function showBookReviews(bookId) {
  const book = books.find(b => b.id === bookId);

  if (!book) return;

  const count = allReviews().filter(r => Number(r.bookId) === bookId).length;

  showToast(`${book.title}: ${count} community review${count === 1 ? "" : "s"} so far.`);
  $("#community").scrollIntoView({behavior:"smooth"});
}

function openReviewDialog(bookId) {
  const select = $("#reviewBook");

  select.innerHTML = books.map(b =>
    `<option value="${b.id}">${escapeHTML(b.title)} - ${escapeHTML(b.author)}</option>`
  ).join("");

  if (bookId) select.value = String(bookId);

  $("#reviewForm").reset();

  if (bookId) select.value = String(bookId);

  activeRating = 5;
  $("#reviewRating").value = "5";
  updateRatingPicker();

  $("#reviewFormMessage").textContent = "";

  const dialog = $("#reviewDialog");

  if (typeof dialog.showModal === "function") {
    dialog.showModal();
  } else {
    dialog.setAttribute("open", "");
  }
}

function closeDialog() {
  const dialog = $("#reviewDialog");

  if (dialog.close) {
    dialog.close();
  } else {
    dialog.removeAttribute("open");
  }
}

function updateRatingPicker() {
  $$("#ratingPicker button").forEach(btn => {
    btn.classList.toggle("selected", Number(btn.dataset.rating) <= activeRating);
  });
}

function showBookReviewModal(bookId) {
  openReviewDialog(bookId);
}

$("#searchInput").addEventListener("input", renderBooks);

$("#genreFilters").addEventListener("click", e => {
  const btn = e.target.closest("[data-genre]");

  if (!btn) return;

  activeGenre = btn.dataset.genre;

  $$("#genreFilters .filter-pill").forEach(p => {
    p.classList.toggle("selected", p === btn);
  });

  renderBooks();
});

["writeReviewTop", "writeReviewCommunity", "writeReviewBottom"].forEach(id => {
  $("#" + id).addEventListener("click", () => openReviewDialog());
});

$("#closeDialog").addEventListener("click", closeDialog);

$("#ratingPicker").addEventListener("click", e => {
  const btn = e.target.closest("[data-rating]");

  if (!btn) return;

  activeRating = Number(btn.dataset.rating);
  $("#reviewRating").value = String(activeRating);

  updateRatingPicker();
});

$("#reviewForm").addEventListener("submit", e => {
  e.preventDefault();

  const name = $("#reviewerName").value.trim();
  const bookId = Number($("#reviewBook").value);
  const text = $("#reviewText").value.trim();

  if (!name || !text || text.length < 12) {
    $("#reviewFormMessage").textContent =
      "Please enter your name and a review of at least 12 characters.";
    return;
  }

  const review = {bookId, name, rating:activeRating, text};

  $("#reviewFormMessage").textContent = "Saving your review...";

  fetch("/api/reviews", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(review)
  }).then(async response => {
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || "The review could not be saved.");
    }

    databaseReviews.unshift(data.review);

    closeDialog();
    renderBooks();
    renderReviews();

    showToast("Thank you. Your review has been saved to the website database.");
  }).catch(error => {
    $("#reviewFormMessage").textContent =
      `${error.message} Make sure you opened the website through the local server.`;
  });
});

/* Newsletter subscription and popup */
$("#newsletterForm").addEventListener("submit", async e => {
  e.preventDefault();

  const email = $("#newsletterEmail").value.trim();
  const message = $("#newsletterMessage");
  const button = e.target.querySelector('button[type="submit"]');

  // Cancel any previous popup timer.
  clearTimeout(newsletterPopupTimer);

  // Make the popup visible.
  message.classList.remove("hidden");
  message.setAttribute("role", "status");
  message.setAttribute("aria-live", "polite");
  message.style.display = "block";

  const originalButtonText = button.textContent;

  button.disabled = true;
  button.textContent = "Joining...";
  message.textContent = "Adding your email...";
  delete message.dataset.status;

  try {
    const response = await fetch("/api/newsletter", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({email})
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || "We couldn't add your email. Please try again.");
    }

    // Show the successful subscription message.
    message.textContent =
      data.message || "You're in! Your email has been added to the BookReview newsletter.";

    message.dataset.status = "success";

    // Clear the email field after successful submission.
    e.target.reset();

    // Automatically hide the popup after five seconds.
    newsletterPopupTimer = setTimeout(() => {
      message.textContent = "";
      message.classList.add("hidden");
      message.style.display = "";
      delete message.dataset.status;
    }, 5000);

  } catch (error) {
    // Show an error popup if the subscription fails.
    message.textContent =
      error.message || "We couldn't complete your subscription. Please try again.";

    message.dataset.status = "error";

    // Automatically hide the error message after five seconds.
    newsletterPopupTimer = setTimeout(() => {
      message.textContent = "";
      message.classList.add("hidden");
      message.style.display = "";
      delete message.dataset.status;
    }, 5000);

  } finally {
    button.disabled = false;
    button.textContent = originalButtonText;
  }
});

$("#menuToggle").addEventListener("click", () => {
  const nav = $("#main-nav") || $(".main-nav");

  if (nav) nav.classList.toggle("open");
});

$$(".main-nav a").forEach(a => {
  a.addEventListener("click", () => $(".main-nav").classList.remove("open"));
});

Promise.all([
  fetch("/api/books").then(r => {
    if (!r.ok) throw new Error("Books could not be loaded");
    return r.json();
  }),
  fetch("/api/reviews").then(r => {
    if (!r.ok) throw new Error("Reviews could not be loaded");
    return r.json();
  })
]).then(([bookData, reviewData]) => {
  if (Array.isArray(bookData.books) && bookData.books.length) {
    books = bookData.books.map(b => ({
      ...b,
      desc: b.desc || b.description || "",
      coverUrl: b.coverUrl || b.cover_url || ""
    }));
  }

  databaseReviews = Array.isArray(reviewData.reviews)
    ? reviewData.reviews
    : [];

  renderBooks();
  renderReviews();

}).catch(() => {
  renderBooks();
  renderReviews();

  showToast("Some live data could not be loaded. Please refresh the page.");
});

updateRatingPicker();


const contactForm = document.getElementById("contactForm");

if (contactForm) {
  contactForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const status = document.getElementById("contactFormStatus");
    const button = contactForm.querySelector('button[type="submit"]');
    const payload = Object.fromEntries(
      new FormData(contactForm).entries()
    );

    status.textContent = "Sending your message...";
    button.disabled = true;

    try {
      const response = await fetch("/api/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Could not send your message.");
      }

      status.textContent = "Message sent successfully. Thank you!";
      contactForm.reset();
    } catch (error) {
      status.textContent =
        error.message || "Something went wrong. Please try again.";
    } finally {
      button.disabled = false;
    }
  });
}


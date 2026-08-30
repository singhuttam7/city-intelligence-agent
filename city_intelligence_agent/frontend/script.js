// ============================================================
// CITY INTELLIGENCE AGENT
// FRONTEND JAVASCRIPT
// ============================================================

// ============================================================
// BACKEND API
// ============================================================

const API_URL =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000/ask"
    : "https://city-intelligence-agent-backend.onrender.com/ask";
// ============================================================
// GET ELEMENTS
// ============================================================

const messageInput = document.getElementById("messageInput");

const chatArea = document.getElementById("chatArea");

const sendBtn = document.getElementById("sendBtn");

const sidebar = document.getElementById("sidebar");

const hamburgerBtn = document.getElementById("hamburgerBtn");

const closeSidebarBtn = document.getElementById("closeSidebarBtn");

const sidebarOverlay = document.getElementById("sidebarOverlay");

const newChatBtn = document.getElementById("newChatBtn");

// ============================================================
// SEND BUTTON
// ============================================================

sendBtn.addEventListener("click", sendMessage);

// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {
  const message = messageInput.value.trim();

  // --------------------------------------------------------
  // Don't send empty message
  // --------------------------------------------------------

  if (!message) {
    messageInput.focus();

    return;
  }

  // --------------------------------------------------------
  // Remove welcome screen
  // --------------------------------------------------------

  const welcome = document.getElementById("welcomeMessage");

  if (welcome) {
    welcome.remove();
  }

  // --------------------------------------------------------
  // Close mobile sidebar
  // --------------------------------------------------------

  closeSidebar();

  // --------------------------------------------------------
  // Display user message
  // --------------------------------------------------------

  addMessage(message, "user");

  // --------------------------------------------------------
  // Clear input
  // --------------------------------------------------------

  messageInput.value = "";

  autoResize();

  // --------------------------------------------------------
  // Disable button
  // --------------------------------------------------------

  sendBtn.disabled = true;

  // --------------------------------------------------------
  // Show typing
  // --------------------------------------------------------

  const typingId = showTyping();

  try {
    // ====================================================
    // BACKEND REQUEST
    // ====================================================

    const response = await fetch(API_URL, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        message: message,
      }),
    });

    // ----------------------------------------------------
    // Check response
    // ----------------------------------------------------

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    // ----------------------------------------------------
    // Convert to JSON
    // ----------------------------------------------------

    const data = await response.json();

    // ----------------------------------------------------
    // Remove typing
    // ----------------------------------------------------

    removeTyping(typingId);

    // ----------------------------------------------------
    // AI RESPONSE
    // ----------------------------------------------------

    if (data.answer !== undefined) {
      addMessage(data.answer, "ai");
    } else {
      addMessage("Sorry, I couldn't generate a response.", "ai");
    }
  } catch (error) {
    console.error("Backend error:", error);

    // ----------------------------------------------------
    // Remove typing
    // ----------------------------------------------------

    removeTyping(typingId);

    // ----------------------------------------------------
    // Error message
    // ----------------------------------------------------

    addMessage(
      "⚠️ Unable to connect to the City Intelligence backend.\n\n" +
        "Please make sure your FastAPI server is running.",

      "ai",
    );
  } finally {
    sendBtn.disabled = false;

    messageInput.focus();
  }
}

// ============================================================
// ADD MESSAGE
// ============================================================

function addMessage(message, sender) {
  const wrapper = document.createElement("div");

  wrapper.className = `message ${sender}`;

  // --------------------------------------------------------
  // Avatar
  // --------------------------------------------------------

  const avatar = document.createElement("div");

  avatar.className = `avatar ${sender === "ai" ? "ai-avatar" : "user-avatar"}`;

  avatar.textContent = sender === "ai" ? "🤖" : "👤";

  // --------------------------------------------------------
  // Content
  // --------------------------------------------------------

  const content = document.createElement("div");

  content.className = "message-content";

  // --------------------------------------------------------
  // User
  // --------------------------------------------------------

  if (sender === "user") {
    content.textContent = message;
  }

  // --------------------------------------------------------
  // AI
  // --------------------------------------------------------
  else {
    content.innerHTML = formatAIResponse(message);
  }

  // --------------------------------------------------------
  // Arrange
  // --------------------------------------------------------

  if (sender === "ai") {
    wrapper.appendChild(avatar);

    wrapper.appendChild(content);
  } else {
    wrapper.appendChild(content);

    wrapper.appendChild(avatar);
  }

  // --------------------------------------------------------
  // Add to chat
  // --------------------------------------------------------

  chatArea.appendChild(wrapper);

  scrollToBottom();
}

// ============================================================
// FORMAT AI RESPONSE
// ============================================================
//
// Removes:
//
// # Heading
// ## Heading
// ### Heading
// **Bold**
// *Italic*
// ---
//
// And converts:
//
// [Read more](https://example.com)
//
// into a real clickable link.
//
// ============================================================

function formatAIResponse(text) {
  if (!text) {
    return "";
  }

  // ========================================================
  // ESCAPE HTML
  // ========================================================

  let output = escapeHTML(text);

  // ========================================================
  // PROTECT MARKDOWN LINKS
  // ========================================================

  const markdownLinks = [];

  output = output.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,

    function (match, linkText, url) {
      const index = markdownLinks.length;

      markdownLinks.push({
        text: linkText,

        url: cleanURL(url),
      });

      return `___MARKDOWN_LINK_${index}___`;
    },
  );

  // ========================================================
  // REMOVE HEADINGS
  // ========================================================

  output = output.replace(
    /^#{1,6}\s*/gm,

    "",
  );

  // ========================================================
  // REMOVE BOLD
  // ========================================================

  output = output.replace(
    /\*\*(.*?)\*\*/g,

    "$1",
  );

  // ========================================================
  // REMOVE ITALIC
  // ========================================================

  output = output.replace(
    /(?<!\*)\*([^*]+)\*(?!\*)/g,

    "$1",
  );

  // ========================================================
  // REMOVE HORIZONTAL LINES
  // ========================================================

  output = output.replace(
    /^-{3,}$/gm,

    "",
  );

  // ========================================================
  // NORMAL URLS
  // ========================================================

  const normalLinks = [];

  output = output.replace(
    /https?:\/\/[^\s<]+/g,

    function (url) {
      const clean = cleanURL(url);

      const punctuation = url.substring(clean.length);

      const index = normalLinks.length;

      normalLinks.push(clean);

      return `___NORMAL_LINK_${index}___` + punctuation;
    },
  );

  // ========================================================
  // CLEAN EMPTY LINES
  // ========================================================

  output = output.replace(
    /^\s*$/gm,

    "",
  );

  // ========================================================
  // CLEAN TRAILING SPACES
  // ========================================================

  output = output.replace(
    /[ \t]+$/gm,

    "",
  );

  // ========================================================
  // NEWLINES
  // ========================================================

  output = output.replace(
    /\n/g,

    "<br>",
  );

  // ========================================================
  // RESTORE MARKDOWN LINKS
  // ========================================================

  markdownLinks.forEach(function (link, index) {
    const html = `

                <a
                    class="ai-link"
                    href="${link.url}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    🔗 ${link.text}
                </a>

            `;

    output = output.replace(
      `___MARKDOWN_LINK_${index}___`,

      html,
    );
  });

  // ========================================================
  // RESTORE NORMAL URLS
  // ========================================================

  normalLinks.forEach(function (url, index) {
    const html = `

                <a
                    class="ai-link"
                    href="${url}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    🔗 Open Source
                </a>

            `;

    output = output.replace(
      `___NORMAL_LINK_${index}___`,

      html,
    );
  });

  return output;
}

// ============================================================
// CLEAN URL
// ============================================================

function cleanURL(url) {
  return url.replace(/[),.!?;:]+$/, "");
}

// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHTML(text) {
  const div = document.createElement("div");

  div.textContent = text;

  return div.innerHTML;
}

// ============================================================
// TYPING INDICATOR
// ============================================================

function showTyping() {
  const id = "typing-" + Date.now();

  const wrapper = document.createElement("div");

  wrapper.id = id;

  wrapper.className = "message ai";

  wrapper.innerHTML = `

        <div class="avatar ai-avatar">
            🤖
        </div>

        <div class="message-content">

            <div class="typing">

                <span></span>

                <span></span>

                <span></span>

            </div>

        </div>

    `;

  chatArea.appendChild(wrapper);

  scrollToBottom();

  return id;
}

// ============================================================
// REMOVE TYPING
// ============================================================

function removeTyping(id) {
  const element = document.getElementById(id);

  if (element) {
    element.remove();
  }
}

// ============================================================
// SCROLL TO BOTTOM
// ============================================================

function scrollToBottom() {
  requestAnimationFrame(function () {
    chatArea.scrollTop = chatArea.scrollHeight;
  });
}

// ============================================================
// USE SUGGESTION
// ============================================================

function useSuggestion(text) {
  messageInput.value = text;

  autoResize();

  // --------------------------------------------------------
  // Close sidebar on mobile
  // --------------------------------------------------------

  if (window.innerWidth <= 768) {
    closeSidebar();
  }

  messageInput.focus();
}

// ============================================================
// NEW CHAT
// ============================================================

newChatBtn.addEventListener("click", function () {
  newChat();

  closeSidebar();
});

function newChat() {
  chatArea.innerHTML = `

        <div
            id="welcomeMessage"
            class="welcome-screen"
        >

            <div class="welcome-logo">
                🤖
            </div>


            <h1>
                Explore Any City
            </h1>


            <p class="welcome-description">

                Ask me about current weather,
                latest news and other city information.

            </p>


            <div class="suggestions">


                <button
                    class="suggestion-card"
                    type="button"
                    onclick="useSuggestion(
                        'What is the current weather in Delhi?'
                    )"
                >

                    <div class="suggestion-icon">
                        🌤️
                    </div>

                    <div class="suggestion-content">

                        <strong>
                            Current Weather
                        </strong>

                        <span>
                            What's the weather in Delhi?
                        </span>

                    </div>

                    <span class="arrow">
                        →
                    </span>

                </button>


                <button
                    class="suggestion-card"
                    type="button"
                    onclick="useSuggestion(
                        'What is the latest news in Mumbai?'
                    )"
                >

                    <div class="suggestion-icon">
                        📰
                    </div>

                    <div class="suggestion-content">

                        <strong>
                            Latest News
                        </strong>

                        <span>
                            Show me the latest news in Mumbai
                        </span>

                    </div>

                    <span class="arrow">
                        →
                    </span>

                </button>


                <button
                    class="suggestion-card"
                    type="button"
                    onclick="useSuggestion(
                        'What is the current temperature in Bangalore?'
                    )"
                >

                    <div class="suggestion-icon">
                        🌡️
                    </div>

                    <div class="suggestion-content">

                        <strong>
                            Temperature
                        </strong>

                        <span>
                            What's the temperature in Bangalore?
                        </span>

                    </div>

                    <span class="arrow">
                        →
                    </span>

                </button>


                <button
                    class="suggestion-card"
                    type="button"
                    onclick="useSuggestion(
                        'Give me the latest news about Delhi'
                    )"
                >

                    <div class="suggestion-icon">
                        🗞️
                    </div>

                    <div class="suggestion-content">

                        <strong>
                            City Updates
                        </strong>

                        <span>
                            Give me the latest Delhi news
                        </span>

                    </div>

                    <span class="arrow">
                        →
                    </span>

                </button>

            </div>


            <div class="quick-label">

                Or type your own question below

            </div>

        </div>

    `;

  messageInput.value = "";

  autoResize();

  messageInput.focus();
}

// ============================================================
// OPEN SIDEBAR
// ============================================================

function openSidebar() {
  if (!sidebar) {
    return;
  }

  sidebar.classList.add("open");

  sidebarOverlay.classList.add("active");

  document.body.classList.add("sidebar-open");

  hamburgerBtn.setAttribute("aria-expanded", "true");
}

// ============================================================
// CLOSE SIDEBAR
// ============================================================

function closeSidebar() {
  if (!sidebar) {
    return;
  }

  sidebar.classList.remove("open");

  sidebarOverlay.classList.remove("active");

  document.body.classList.remove("sidebar-open");

  hamburgerBtn.setAttribute("aria-expanded", "false");
}

// ============================================================
// TOGGLE SIDEBAR
// ============================================================

function toggleSidebar() {
  if (sidebar.classList.contains("open")) {
    closeSidebar();
  } else {
    openSidebar();
  }
}

// ============================================================
// HAMBURGER CLICK
// ============================================================

hamburgerBtn.addEventListener(
  "click",

  function (event) {
    event.stopPropagation();

    toggleSidebar();
  },
);

// ============================================================
// CLOSE BUTTON CLICK
// ============================================================

closeSidebarBtn.addEventListener(
  "click",

  function (event) {
    event.stopPropagation();

    closeSidebar();
  },
);

// ============================================================
// OVERLAY CLICK
// ============================================================
//
// Tapping outside the sidebar closes it.
// This is especially important on mobile.
//

sidebarOverlay.addEventListener(
  "click",

  function () {
    closeSidebar();
  },
);

// ============================================================
// ESCAPE KEY
// ============================================================

document.addEventListener(
  "keydown",

  function (event) {
    if (event.key === "Escape") {
      closeSidebar();
    }
  },
);

// ============================================================
// CLOSE SIDEBAR WHEN MOBILE SIDEBAR ITEM IS CLICKED
// ============================================================

const sidebarItems = document.querySelectorAll(".sidebar-item");

sidebarItems.forEach(function (item) {
  item.addEventListener("click", function () {
    if (window.innerWidth <= 768) {
      closeSidebar();
    }
  });
});

// ============================================================
// RESIZE HANDLER
// ============================================================

window.addEventListener(
  "resize",

  function () {
    // ----------------------------------------------------
    // If moved to desktop, reset mobile sidebar state.
    // ----------------------------------------------------

    if (window.innerWidth > 768) {
      closeSidebar();
    }
  },
);

// ============================================================
// AUTO RESIZE TEXTAREA
// ============================================================

messageInput.addEventListener(
  "input",

  autoResize,
);

function autoResize() {
  messageInput.style.height = "auto";

  messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
}

// ============================================================
// ENTER / SHIFT + ENTER
// ============================================================

messageInput.addEventListener(
  "keydown",

  function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      sendMessage();
    }
  },
);

// ============================================================
// INITIALIZE
// ============================================================

autoResize();

messageInput.focus();

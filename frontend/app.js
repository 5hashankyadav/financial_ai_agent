const API_URL = "http://127.0.0.1:8000";

// DOM Elements
const questionInput = document.getElementById("question");
const roleInput = document.getElementById("role");
const askButton = document.getElementById("askButton");
const buttonText = document.getElementById("buttonText");
const spinner = document.getElementById("spinner");

const answerSection = document.getElementById("answerSection");
const emptyState = document.getElementById("emptyState");

const answerElement = document.getElementById("answer");
const routeBadge = document.getElementById("routeBadge");

const sourcesElement = document.getElementById("sources");
const sourceCount = document.getElementById("sourceCount");
const errorBox = document.getElementById("errorBox");

const iphoneButton = document.getElementById("iphoneButton");
const revenueButton = document.getElementById("revenueButton");
const strategyButton = document.getElementById("strategyButton");
const restrictTestButton = document.getElementById("restrictTestButton");
const copyAnswerBtn = document.getElementById("copyAnswerBtn");

const historyList = document.getElementById("historyList");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");

// Feedback Elements
const thumbsUpBtn = document.getElementById("thumbsUpBtn");
const thumbsDownBtn = document.getElementById("thumbsDownBtn");
const correctionBox = document.getElementById("correctionBox");
const correctionInput = document.getElementById("correctionInput");
const submitFeedbackBtn = document.getElementById("submitFeedbackBtn");
const feedbackMsg = document.getElementById("feedbackMsg");

console.log("Financial AI Enterprise Frontend loaded");

/* ==================================================
   QUERY HISTORY MANAGEMENT
================================================== */

function getQueryHistory() {
    try {
        return JSON.parse(localStorage.getItem("financial_query_history")) || [];
    } catch {
        return [];
    }
}

function saveQueryHistory(query) {
    let history = getQueryHistory();
    history = history.filter(q => q.toLowerCase() !== query.toLowerCase());
    history.unshift(query);
    if (history.length > 5) history = history.slice(0, 5);
    localStorage.setItem("financial_query_history", JSON.stringify(history));
    renderQueryHistory();
}

function renderQueryHistory() {
    if (!historyList) return;
    const history = getQueryHistory();

    if (history.length === 0) {
        historyList.innerHTML = '<div class="history-empty">No previous queries</div>';
        return;
    }

    historyList.innerHTML = "";
    history.forEach(query => {
        const chip = document.createElement("div");
        chip.className = "history-chip";
        chip.innerHTML = `<span class="history-icon"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg></span><span class="history-text">${query}</span>`;
        chip.addEventListener("click", () => {
            questionInput.value = query;
            questionInput.focus();
        });
        historyList.appendChild(chip);
    });
}

if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", () => {
        localStorage.removeItem("financial_query_history");
        renderQueryHistory();
    });
}

renderQueryHistory();

/* ==================================================
   QUICK PROMPT HANDLERS
================================================== */

if (iphoneButton) {
    iphoneButton.addEventListener("click", () => {
        questionInput.value = "What was Apple's iPhone revenue in Q1 FY25?";
        questionInput.focus();
    });
}

if (revenueButton) {
    revenueButton.addEventListener("click", () => {
        questionInput.value = "Why did Apple's revenue change from Q2 FY25 to Q3 FY25?";
        questionInput.focus();
    });
}

if (strategyButton) {
    strategyButton.addEventListener("click", () => {
        questionInput.value = "What does Apple's annual report say about its business strategy?";
        questionInput.focus();
    });
}

if (restrictTestButton) {
    restrictTestButton.addEventListener("click", () => {
        questionInput.value = "What is Apple's total headcount and employee compensation?";
        questionInput.focus();
    });
}

/* ==================================================
   LOADING & ERROR STATES
================================================== */

function setLoading(isLoading) {
    askButton.disabled = isLoading;
    if (isLoading) {
        buttonText.textContent = "Analyzing...";
        spinner.classList.remove("hidden");
    } else {
        buttonText.textContent = "Analyze Query";
        spinner.classList.add("hidden");
    }
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function hideError() {
    errorBox.textContent = "";
    errorBox.classList.add("hidden");
}

/* ==================================================
   ASK AGENT QUERY EXECUTION
================================================== */

async function askQuestion() {
    hideError();
    resetFeedbackUI();

    const question = questionInput.value.trim();
    const role = roleInput.value;

    if (!question) {
        showError("Please enter a financial question.");
        questionInput.focus();
        return;
    }

    setLoading(true);

    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question, role: role })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Financial agent returned an error.");
        }

        saveQueryHistory(question);
        displayAnswer(data);

    } catch (error) {
        console.error("Request failed:", error);
        showError(error.message || "Unable to connect to the Financial AI Agent API.");
    } finally {
        setLoading(false);
    }
}

askButton.addEventListener("click", askQuestion);

/* ==================================================
   FORMAT & DISPLAY ANSWER
================================================== */

function formatAnswer(text) {
    if (!text) return "No answer returned.";

    let formatted = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Bold text **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Bullets
    formatted = formatted.replace(/^\s*\*\s+/gm, "• ");

    // Italic *text*
    formatted = formatted.replace(/(?<!\*)\*(?!\*)(.*?)\*(?!\*)/g, "<em>$1</em>");

    // Newlines
    formatted = formatted.replace(/\n/g, "<br>");

    return formatted;
}

function displayAnswer(data) {
    if (emptyState) emptyState.classList.add("hidden");
    answerSection.classList.remove("hidden");

    answerElement.innerHTML = formatAnswer(data.answer || "No answer returned.");

    const routeStr = (data.route || "unknown").toLowerCase();
    routeBadge.textContent = data.route || "unknown";

    if (routeStr.includes("structured")) {
        routeBadge.className = "route-badge structured";
        routeBadge.textContent = "Structured DB";
    } else if (routeStr.includes("hybrid")) {
        routeBadge.className = "route-badge hybrid";
        routeBadge.textContent = "Hybrid Search";
    } else if (routeStr.includes("rag")) {
        routeBadge.className = "route-badge rag";
        routeBadge.textContent = "PDF Retrieval";
    } else {
        routeBadge.className = "route-badge";
    }

    renderSources(data.sources || []);

    answerSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

/* ==================================================
   RENDER SOURCES GRID
================================================== */

function renderSources(sources) {
    sourcesElement.innerHTML = "";
    sourceCount.textContent = `${sources.length} ${sources.length === 1 ? "source" : "sources"}`;

    if (sources.length === 0) {
        const empty = document.createElement("div");
        empty.className = "source-card";
        empty.textContent = "No external document sources required for this query.";
        sourcesElement.appendChild(empty);
        return;
    }

    sources.forEach(source => {
        const card = document.createElement("div");
        card.className = "source-card";

        const file = document.createElement("div");
        file.className = "source-file";
        file.textContent = `📄 ${source.source_file || "Unknown Source"}`;

        const meta = document.createElement("div");
        meta.className = "source-meta";

        if (source.source_sheet) {
            const sheet = document.createElement("span");
            sheet.textContent = `Sheet: ${source.source_sheet}`;
            meta.appendChild(sheet);
        }

        if (source.source_row !== null && source.source_row !== undefined) {
            const row = document.createElement("span");
            row.textContent = `Row: ${source.source_row}`;
            meta.appendChild(row);
        }

        if (source.page_number !== null && source.page_number !== undefined) {
            const page = document.createElement("span");
            page.textContent = `Page: ${source.page_number}`;
            meta.appendChild(page);
        }

        if (source.score !== null && source.score !== undefined) {
            const score = document.createElement("span");
            score.textContent = `Relevance: ${Math.round(source.score * 100)}%`;
            meta.appendChild(score);
        }

        card.appendChild(file);
        card.appendChild(meta);
        sourcesElement.appendChild(card);
    });
}

/* ==================================================
   COPY ANSWER TO CLIPBOARD
================================================== */

if (copyAnswerBtn) {
    copyAnswerBtn.addEventListener("click", () => {
        const text = answerElement.innerText;
        navigator.clipboard.writeText(text).then(() => {
            copyAnswerBtn.textContent = "✓ Copied!";
            setTimeout(() => {
                copyAnswerBtn.textContent = "📋 Copy";
            }, 2000);
        });
    });
}

/* ==================================================
   CTRL + ENTER KEYBIND
================================================== */

questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        askQuestion();
    }
});

/* ==================================================
   FEEDBACK WIDGET HANDLING
================================================== */

function resetFeedbackUI() {
    if (correctionBox) correctionBox.classList.add("hidden");
    if (feedbackMsg) {
        feedbackMsg.classList.add("hidden");
        feedbackMsg.textContent = "";
    }
    if (correctionInput) correctionInput.value = "";
}

if (thumbsUpBtn) {
    thumbsUpBtn.addEventListener("click", () => sendFeedback(1, ""));
}

if (thumbsDownBtn) {
    thumbsDownBtn.addEventListener("click", () => {
        if (correctionBox) {
            correctionBox.classList.remove("hidden");
            correctionInput.focus();
        }
    });
}

if (submitFeedbackBtn) {
    submitFeedbackBtn.addEventListener("click", () => {
        const correction = correctionInput.value.trim();
        sendFeedback(-1, correction);
    });
}

async function sendFeedback(rating, correction) {
    const question = questionInput.value.trim();
    const role = roleInput.value;
    const route = routeBadge.textContent.trim();
    const answer = answerElement.innerText.trim();

    try {
        const response = await fetch(`${API_URL}/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: question,
                role: role,
                rating: rating,
                route: route,
                answer: answer,
                correction: correction,
            })
        });

        if (response.ok) {
            if (feedbackMsg) {
                feedbackMsg.textContent = rating > 0 
                    ? "✓ Feedback recorded! Thank you for helping the agent learn." 
                    : "✓ Correction stored in agent memory!";
                feedbackMsg.classList.remove("hidden");
            }
            if (correctionBox) correctionBox.classList.add("hidden");
        }
    } catch (e) {
        console.error("Failed to submit feedback", e);
    }
}

/* ==================================================
   API HEALTH CHECK ON INITIAL LOAD
================================================== */

async function checkAPI() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) throw new Error();
        console.log("Financial AI API connected and healthy.");
    } catch {
        console.warn("Financial AI API is not reachable.");
    }
}

checkAPI();
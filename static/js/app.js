const analyzeBtn = document.getElementById("analyzeBtn");
const resumeTextEl = document.getElementById("resumeText");
const jobDescriptionEl = document.getElementById("jobDescription");
const resultsSection = document.getElementById("results");
const errorEl = document.getElementById("error");
const candidateNameEl = document.getElementById("candidateName");
const overallSummaryEl = document.getElementById("overallSummary");
const tagListEl = document.getElementById("tagList");
const matrixBodyEl = document.getElementById("matrixBody");
const recommendationsListEl = document.getElementById("recommendationsList");
const rowTemplate = document.getElementById("skillRowTemplate");

async function analyzeResume() {
  errorEl.hidden = true;
  errorEl.textContent = "";
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";

  try {
    const payload = {
      resumeText: resumeTextEl.value,
      jobDescription: jobDescriptionEl.value,
    };

    const response = await fetch("/api/parse_resume", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to parse resume");
    }

    renderResults(data);
  } catch (error) {
    errorEl.hidden = false;
    errorEl.textContent = error.message;
    resultsSection.hidden = true;
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze Resume";
  }
}

function renderResults(data) {
  const {
    candidate_name: candidateName = "Candidate",
    overall_summary: overallSummary = "",
    tags = [],
    skills = [],
    recommendations = [],
  } = data;

  candidateNameEl.textContent = candidateName || "Candidate";
  overallSummaryEl.textContent = overallSummary;

  tagListEl.innerHTML = "";
  tags.forEach((tag) => {
    const item = document.createElement("li");
    item.className = "tag";
    item.dataset.status = tag.status || "medium";
    item.innerHTML = `<span>${tag.label}</span><strong>${formatScore(tag.score)}</strong>`;
    tagListEl.appendChild(item);
  });

  matrixBodyEl.innerHTML = "";
  skills.forEach((skill) => {
    const clone = rowTemplate.content.cloneNode(true);
    const row = clone.querySelector(".matrix-row");
    row.querySelector(".category").textContent = skill.category || "";

    populateList(row.querySelector(".strengths"), skill.strengths);
    populateList(row.querySelector(".weaknesses"), skill.weaknesses);

    const scoreEl = row.querySelector(".score");
    scoreEl.textContent = formatScore(skill.score);

    matrixBodyEl.appendChild(clone);
  });

  recommendationsListEl.innerHTML = "";
  recommendations.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    recommendationsListEl.appendChild(li);
  });

  resultsSection.hidden = false;
  resultsSection.scrollIntoView({ behavior: "smooth" });
}

function populateList(listEl, items) {
  listEl.innerHTML = "";
  if (!items || !items.length) {
    const empty = document.createElement("li");
    empty.textContent = "-";
    empty.className = "muted";
    listEl.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    listEl.appendChild(li);
  });
}

function formatScore(score) {
  if (typeof score === "number" && !Number.isNaN(score)) {
    return `${score.toFixed(1)}/5`;
  }
  return "-";
}

analyzeBtn.addEventListener("click", analyzeResume);

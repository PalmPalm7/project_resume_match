import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import axios from "axios";

interface EducationEntry {
  institution: string;
  degree: string;
  start_year: string;
  end_year: string;
  highlights: string[];
}

interface ExperienceEntry {
  company: string;
  role: string;
  start_date: string;
  end_date: string;
  highlights: string[];
  skills_demonstrated: string[];
}

interface SkillsMatrix {
  core: string[];
  tools: string[];
}

interface ResumeInsightsResponse {
  candidate_name: string;
  headline: string;
  contact_information: string;
  education: EducationEntry[];
  experience: ExperienceEntry[];
  skills: SkillsMatrix;
  strengths: string[];
  weaknesses: string[];
  overall_summary: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function formatList(items: string[] | undefined): string {
  if (!items || items.length === 0) {
    return "-";
  }
  return items.join(", ");
}

function App() {
  const [apiKey, setApiKey] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResumeInsightsResponse | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setResult(null);

    if (!apiKey) {
      setError("Please provide your OpenAI API key.");
      return;
    }

    if (!file) {
      setError("Please upload a resume file.");
      return;
    }

    const formData = new FormData();
    formData.append("api_key", apiKey);
    formData.append("file", file);

    try {
      setIsLoading(true);
      const response = await axios.post<ResumeInsightsResponse>(
        `${API_BASE}/api/process-resume`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data"
          }
        }
      );
      setResult(response.data);
    } catch (err: any) {
      const message = err?.response?.data?.detail ?? err.message ?? "Unknown error";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const strengths = useMemo(() => result?.strengths ?? [], [result]);
  const weaknesses = useMemo(() => result?.weaknesses ?? [], [result]);

  return (
    <div className="container">
      <header>
        <h1>Resume Intelligence</h1>
        <p>
          Upload a PDF or DOCX resume and generate a structured profile with strengths and
          weaknesses using OpenAI.
        </p>
      </header>

      <form className="resume-form" onSubmit={handleSubmit}>
        <label>
          OpenAI API Key
          <input
            type="password"
            placeholder="sk-..."
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            required
          />
        </label>

        <label className="file-input">
          Resume File
          <input type="file" accept=".pdf,.docx" onChange={handleFileChange} required />
        </label>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze Resume"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <section className="results">
          <div className="summary-card">
            <h2>{result.candidate_name || "Candidate"}</h2>
            <p className="headline">{result.headline}</p>
            <p className="contact">{result.contact_information}</p>
            <p>{result.overall_summary}</p>
          </div>

          <div className="matrix-grid">
            <div className="grid-card">
              <h3>Education</h3>
              {result.education.length === 0 && <p>No education details found.</p>}
              {result.education.map((entry, index) => (
                <div className="grid-section" key={`${entry.institution}-${index}`}>
                  <h4>{entry.institution}</h4>
                  <p>{entry.degree}</p>
                  <p>
                    {entry.start_year} - {entry.end_year}
                  </p>
                  <p>{formatList(entry.highlights)}</p>
                </div>
              ))}
            </div>

            <div className="grid-card">
              <h3>Experience</h3>
              {result.experience.length === 0 && <p>No experience details found.</p>}
              {result.experience.map((entry, index) => (
                <div className="grid-section" key={`${entry.company}-${index}`}>
                  <h4>{entry.role}</h4>
                  <p>{entry.company}</p>
                  <p>
                    {entry.start_date} - {entry.end_date}
                  </p>
                  <p>{formatList(entry.highlights)}</p>
                  <p className="skills-label">Skills: {formatList(entry.skills_demonstrated)}</p>
                </div>
              ))}
            </div>

            <div className="grid-card">
              <h3>Skills</h3>
              <div className="grid-section">
                <h4>Core</h4>
                <p>{formatList(result.skills.core)}</p>
              </div>
              <div className="grid-section">
                <h4>Tools</h4>
                <p>{formatList(result.skills.tools)}</p>
              </div>
            </div>

            <div className="grid-card">
              <h3>Strengths & Weaknesses</h3>
              <div className="grid-section list-section">
                <h4>Strengths</h4>
                <ul>
                  {strengths.map((item, index) => (
                    <li key={`strength-${index}`}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="grid-section list-section">
                <h4>Weaknesses</h4>
                <ul>
                  {weaknesses.map((item, index) => (
                    <li key={`weakness-${index}`}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default App;

import React, { useState, useEffect } from "react";
import Cookies from "js-cookie";
import { postExperience, getFrameworks } from "../utils/api";
import { useNavigate } from "react-router-dom";

const ShareExperiencePage = () => {
  const [selectedFramework, setSelectedFramework] = useState("");
  const [experienceText, setExperienceText] = useState("");
  const [error, setError] = useState("");
  const token = Cookies.get("token");
  const navigate = useNavigate();
  const [frameworks, setFrameworks] = useState([]);

  useEffect((navigate) => {
    const token = Cookies.get("token");

    if (token) {
      getFrameworks(token)
        .then((data) => setFrameworks(data))
        .catch((error) => console.error("Error fetching frameworks", error));
    } else navigate("/");
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await postExperience(token, {
        web_framework: selectedFramework,
        text: experienceText,
      });
      navigate("/home");
    } catch (err) {
        setError(err.response?.data?.error ? err.response.data.error : "Something went wrong.")
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Share your experience with the WEB ..</h1>

      <button
        onClick={() => navigate("/home")}
        style={styles.homeButton}
      >
        Home
      </button>

      {error && <div style={styles.error}>{error}</div>}

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.inputGroup}>
          <label style={styles.label}>Choose Framework</label>
          <select
            onChange={(e) => setSelectedFramework(e.target.value)}
            value={selectedFramework}
            required
            style={styles.select}
          >
            <option value="">Select a Framework</option>
            {frameworks.map((fw) => (
              <option key={fw.id} value={fw.id}>
                {fw.name}
              </option>
            ))}
          </select>
        </div>
        <div style={styles.inputGroup}>
          <label style={styles.label}>Experience Text</label>
          <textarea
            value={experienceText}
            onChange={(e) => setExperienceText(e.target.value)}
            required
            style={styles.textarea}
            maxlength={500}
          />
        </div>
        <button type="submit" style={styles.button}>
          Submit Experience
        </button>
      </form>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "500px",
    margin: "50px auto",
    padding: "20px",
    border: "1px solid #ddd",
    borderRadius: "8px",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    backgroundColor: "#fff",
  },
  title: {
    textAlign: "center",
    fontSize: "24px",
    marginBottom: "20px",
    color: "#333",
  },
  error: {
    color: "red",
    marginBottom: "16px",
    textAlign: "center",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  inputGroup: {
    display: "flex",
    flexDirection: "column",
  },
  label: {
    marginBottom: "8px",
    fontSize: "14px",
    color: "#555",
  },
  select: {
    padding: "10px",
    fontSize: "14px",
    border: "1px solid #ccc",
    borderRadius: "4px",
    outline: "none",
    transition: "border-color 0.3s",
  },
  textarea: {
    padding: "10px",
    fontSize: "14px",
    border: "1px solid #ccc",
    borderRadius: "4px",
    outline: "none",
    resize: "vertical",
    minHeight: "100px",
    transition: "border-color 0.3s",
  },
  button: {
    padding: "10px 16px",
    fontSize: "16px",
    color: "#fff",
    backgroundColor: "#007BFF",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    transition: "background-color 0.3s",
  },

  homeButton: {
    position: "fixed",
    top: "16px",
    right: "16px",
    backgroundColor: "#007BFF",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "8px 16px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "bold",
    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
    zIndex: "1000"
  },
};

export default ShareExperiencePage;

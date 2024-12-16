import React, { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { getExperiences, getFrameworks } from "../utils/api";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const [experiences, setExperiences] = useState([]);
  const [frameworks, setFrameworks] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect((navigate) => {
    const token = Cookies.get("token");
  
    if (token) {
      Promise.all([getFrameworks(token), getExperiences(token)])
        .then(([frameworksData, experiencesData]) => {
          setFrameworks(frameworksData);
          setExperiences(experiencesData);
        })
        .catch(() => navigate("/"))
        .finally(() => setLoading(false));
    } else {
      navigate("/");
    }
  }, [navigate]);

  if (loading) {
    return <div style={{ textAlign: "center", marginTop: "50px" }}>Loading...</div>;
  }

  return (
    <div style={{ position: "relative" }}>

      <button
        onClick={() => navigate("/share-experience")}
        style={{
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
          zIndex: "1000",
        }}
      >
        Share your thoughts
      </button>

      <div style={{ maxWidth: "600px", margin: "0 auto", padding: "16px" }}>
        <h1 style={{ textAlign: "center", marginTop: "50px" }}>What do other WEB devs think 💭</h1>

        <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "16px" }}>
          {experiences.map((experience) => {
            const framework = frameworks.find(
              (fw) => fw.id === experience.web_framework
            );

            return (
              <div
                key={experience.id}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  padding: "16px",
                  position: "relative",
                  wordWrap: "break-word",
                  backgroundColor: "#f9f9f9",
                }}
              >
                {experience.hot && (
                  <span
                    role="img"
                    aria-label="fire"
                    style={{
                      position: "absolute",
                      top: "8px",
                      right: "8px",
                      fontSize: "24px",
                      cursor: "pointer",
                    }}
                  >
                    🔥
                  </span>
                )}
                <p>
                  <strong>Owner:</strong> {experience.owner === 1 ? "Admin" : "Guest"}
                </p>
                <p style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <strong>Framework:</strong>
                  {framework && (
                    <>
                      {framework.name}
                      {framework.icon && (
                        <img
                          src={framework.icon}
                          alt={`${framework.name} logo`}
                          style={{
                            width: "25px",
                            height: "25px",
                            borderRadius: "50%",
                            marginLeft: "10px",
                          }}
                        />
                      )}
                    </>
                  )}
                </p>
                <p style={{ marginTop: "12px" }}>{experience.text}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default HomePage;

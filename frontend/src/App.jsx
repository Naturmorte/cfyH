import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

const USER_ID = "demo-user";
const API_URL =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

function App() {
  const [complaints, setComplaints] = useState([]);
  const [health, setHealth] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchComplaints = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/complaints`, {
        params: { user_id: USER_ID }
      });
      setComplaints(res.data);
    } catch (err) {
      console.error(err);
      setError("Помилка завантаження скарг");
    }
  };

  const fetchHealth = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/health-indicators`, {
        params: { user_id: USER_ID }
      });
      setHealth(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchComplaints();
    fetchHealth();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await axios.post(`${API_URL}/api/complaints`, {
        user_id: USER_ID,
        text
      });
      setText("");
      setComplaints((prev) => [...prev, res.data]);
      fetchHealth();
    } catch (err) {
      console.error(err);
      setError("Не вдалося створити скаргу");
    } finally {
      setLoading(false);
    }
  };

  const chartData = useMemo(() => {
    const counts = {};
    complaints.forEach((c) => {
      if (!c.created_at) return;
      const date = new Date(c.created_at).toISOString().slice(0, 10);
      counts[date] = (counts[date] || 0) + 1;
    });
    return Object.entries(counts)
      .sort(([d1], [d2]) => (d1 < d2 ? -1 : 1))
      .map(([date, count]) => ({ date, count }));
  }, [complaints]);

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "1.5rem",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif"
      }}
    >
      <h1 style={{ fontSize: "1.8rem", marginBottom: "1rem" }}>
        Цифровий щоденник здоров’я (MVP)
      </h1>

      {/* Форма введення скарги */}
      <section
        style={{
          marginBottom: "1.5rem",
          padding: "1rem",
          border: "1px solid #ddd",
          borderRadius: "8px"
        }}
      >
        <h2 style={{ marginBottom: "0.5rem", fontSize: "1.2rem" }}>
          Нова скарга
        </h2>
        <form onSubmit={handleSubmit}>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Опишіть свою скаргу..."
            rows={3}
            style={{
              width: "100%",
              padding: "0.5rem",
              marginBottom: "0.5rem",
              resize: "vertical"
            }}
          />
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}
          >
            <small>
              User ID: <strong>{USER_ID}</strong>
            </small>
            <button type="submit" disabled={loading}>
              {loading ? "Збереження..." : "Додати скаргу"}
            </button>
          </div>
        </form>
        {error && (
          <p style={{ color: "red", marginTop: "0.5rem" }}>{error}</p>
        )}
      </section>

      {/* Індикатор здоров’я */}
      <section
        style={{
          marginBottom: "1.5rem",
          padding: "1rem",
          border: "1px solid #ddd",
          borderRadius: "8px"
        }}
      >
        <h2 style={{ marginBottom: "0.5rem", fontSize: "1.2rem" }}>
          Індикатор здоров’я
        </h2>
        {health ? (
          <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
            <div>
              <div>Health Score:</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
                {health.health_score}
              </div>
            </div>
            <div>
              <div>Total complaints:</div>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
                {health.total_complaints}
              </div>
            </div>
            <div>
              <div>Last complaint:</div>
              <div>
                {health.last_complaint_date
                  ? new Date(health.last_complaint_date).toLocaleString()
                  : "-"}
              </div>
            </div>
          </div>
        ) : (
          <p>Немає даних.</p>
        )}
      </section>

      {/* Графік динаміки */}
      <section
        style={{
          marginBottom: "1.5rem",
          padding: "1rem",
          border: "1px solid #ddd",
          borderRadius: "8px"
        }}
      >
        <h2 style={{ marginBottom: "0.5rem", fontSize: "1.2rem" }}>
          Динаміка скарг
        </h2>
        {chartData.length ? (
          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Line type="monotone" dataKey="count" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p>Поки що немає скарг для побудови графіка.</p>
        )}
      </section>

      {/* Список скарг */}
      <section
        style={{
          marginBottom: "1.5rem",
          padding: "1rem",
          border: "1px solid #ddd",
          borderRadius: "8px"
        }}
      >
        <h2 style={{ marginBottom: "0.5rem", fontSize: "1.2rem" }}>
          Список скарг
        </h2>
        {complaints.length === 0 ? (
          <p>Скарг ще немає.</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {complaints.map((c) => (
              <li
                key={c.id}
                style={{ borderBottom: "1px solid #eee", padding: "0.5rem 0" }}
              >
                <div style={{ fontSize: "0.9rem", color: "#555" }}>
                  {c.created_at
                    ? new Date(c.created_at).toLocaleString()
                    : ""}
                </div>
                <div style={{ margin: "0.25rem 0" }}>{c.text}</div>
                <div style={{ fontSize: "0.85rem", color: "#333" }}>
                  ICPC: <strong>{c.icpc_code || "-"}</strong> | ICD-11:{" "}
                  <strong>{c.icd_code || "-"}</strong>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default App;

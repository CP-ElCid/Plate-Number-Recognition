import { useState } from "react";
import axios from "axios";

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleLogin = async (e: any) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://127.0.0.1:8000/api/auth/login", new URLSearchParams({
        username: form.username,
        password: form.password
      }));
      localStorage.setItem("token", res.data.access_token);
      window.location.href = "/";
    } catch {
      setError("Invalid credentials");
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0a0a',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem'
    }}>
      <div style={{
        background: '#1f2937',
        borderRadius: '24px',
        padding: '3rem',
        width: '100%',
        maxWidth: '450px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
      }}>
        {/* Car Icon */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
          <div style={{
            background: '#374151',
            borderRadius: '16px',
            padding: '1.5rem',
            width: '120px',
            height: '120px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg
              style={{ width: '80px', height: '80px', color: 'white' }}
              fill="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
            </svg>
          </div>
        </div>

        {/* Title */}
        <h2 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          color: 'white',
          textAlign: 'center',
          marginBottom: '2rem'
        }}>Login</h2>

        {/* Form */}
        <form onSubmit={handleLogin}>
          <input
            placeholder="Username"
            value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })}
            style={{
              width: '100%',
              background: '#374151',
              color: 'white',
              fontSize: '1.125rem',
              padding: '1rem',
              borderRadius: '12px',
              border: 'none',
              marginBottom: '1rem',
              outline: 'none'
            }}
            required
          />
          <input
            placeholder="Password"
            type="password"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            style={{
              width: '100%',
              background: '#374151',
              color: 'white',
              fontSize: '1.125rem',
              padding: '1rem',
              borderRadius: '12px',
              border: 'none',
              marginBottom: '1.5rem',
              outline: 'none'
            }}
            required
          />

          <button
            type="submit"
            style={{
              width: '100%',
              background: '#2563eb',
              color: 'white',
              fontSize: '1.25rem',
              fontWeight: '600',
              padding: '1rem',
              borderRadius: '12px',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.2s'
            }}
            onMouseOver={e => e.currentTarget.style.background = '#1d4ed8'}
            onMouseOut={e => e.currentTarget.style.background = '#2563eb'}
          >
            Login
          </button>

          {/* Forgot Password Link */}
          <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
            <a
              href="#"
              style={{
                color: '#60a5fa',
                fontSize: '1.125rem',
                textDecoration: 'none'
              }}
              onMouseOver={e => e.currentTarget.style.color = '#93c5fd'}
              onMouseOut={e => e.currentTarget.style.color = '#60a5fa'}
            >
              Forgot password?
            </a>
          </div>

          {/* Error Message */}
          {error && (
            <p style={{
              color: '#f87171',
              textAlign: 'center',
              marginTop: '1rem',
              background: 'rgba(153, 27, 27, 0.2)',
              padding: '0.75rem',
              borderRadius: '8px'
            }}>
              {error}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

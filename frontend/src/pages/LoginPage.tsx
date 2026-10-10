import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { ShieldCheck, AlertCircle } from "lucide-react";
import loginBackground from "../assets/login-background.avif";

export const LoginPage: React.FC = () => {
  const { login, signup } = useAuth();
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<"officer" | "borrower">("officer");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      if (isSignup) {
        await signup({ username, email, password, full_name: fullName, role });
      } else {
        await login(username, password);
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="relative min-h-screen bg-[#14243A] flex flex-col justify-center items-center px-4 py-12 overflow-hidden"
      style={{
        backgroundImage: `url(${loginBackground})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div className="absolute inset-0 bg-[#14243A]/70" aria-hidden="true" />
      <div className="relative z-10 max-w-md w-full space-y-8">
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-xl bg-[#0D9488] mx-auto flex items-center justify-center shadow-md">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">CREDENCE <span className="text-[#5EEAD4]">AI</span></h1>
          <p className="text-xs text-white/80 max-w-xs mx-auto">
            Explainable Alternative Credit Scoring & Informal Income Synthesizer
          </p>
        </div>

        {/* Login Form Card */}
        <div className="bg-white/95 backdrop-blur-sm border border-white/60 p-8 rounded-2xl shadow-card space-y-6">
          <div className="flex border-b border-slate-200 pb-3">
            <button
              onClick={() => { setIsSignup(false); setError(null); }}
              className={`flex-1 text-center py-2 text-xs font-bold transition-all ${
                !isSignup ? "text-[#0D9488] border-b-2 border-[#0D9488]" : "text-slate-400 hover:text-slate-600"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setIsSignup(true); setError(null); }}
              className={`flex-1 text-center py-2 text-xs font-bold transition-all ${
                isSignup ? "text-[#0D9488] border-b-2 border-[#0D9488]" : "text-slate-400 hover:text-slate-600"
              }`}
            >
              Register
            </button>
          </div>

          {error && (
            <div className="bg-rose-50 border border-rose-200 p-3.5 rounded-xl text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            {isSignup && (
              <>
                <div>
                  <label className="block text-slate-700 mb-1 font-semibold">Full Name</label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Sarah Jenkins"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3.5 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#0D9488] focus:bg-white transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 mb-1 font-semibold">Email Address</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="officer@credence.ai"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3.5 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#0D9488] focus:bg-white transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 mb-1 font-semibold">Account Role</label>
                  <select
                    value={role}
                    onChange={(e: any) => setRole(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3.5 py-2.5 text-slate-900 focus:outline-none focus:border-[#0D9488] focus:bg-white transition-colors font-medium"
                  >
                    <option value="officer">Loan Officer</option>
                    <option value="borrower">Borrower</option>
                  </select>
                </div>
              </>
            )}

            <div>
              <label className="block text-slate-700 mb-1 font-semibold">Username</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3.5 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#0D9488] focus:bg-white transition-colors"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1 font-semibold">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3.5 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#0D9488] focus:bg-white transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-[#0D9488] hover:bg-[#0F766E] text-white font-bold text-xs rounded-lg transition-all shadow-sm disabled:opacity-50 mt-2"
            >
              {submitting ? "Authenticating..." : isSignup ? "Create Account" : "Sign In"}
            </button>
          </form>
        </div>

        <p className="text-center text-[11px] text-white/75 font-medium">
          Credence AI — Secure Underwriting Portal
        </p>
      </div>
    </div>
  );
};

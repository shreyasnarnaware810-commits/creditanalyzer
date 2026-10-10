import React from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Scale,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import siteBackground from "../assets/site-background.jpg";

const capabilities = [
  {
    icon: BarChart3,
    title: "See the full signal",
    text: "Bring transaction, utility, and informal income patterns into one focused underwriting view.",
  },
  {
    icon: Scale,
    title: "Make it explainable",
    text: "Turn scores into clear factor-level context that officers and borrowers can understand.",
  },
  {
    icon: ShieldCheck,
    title: "Keep decisions accountable",
    text: "Track data quality, fairness indicators, and the decision trail in one secure workspace.",
  },
];

export const LandingPage: React.FC = () => {
  return (
    <div
      className="relative min-h-screen overflow-hidden bg-[#071C2F] text-white"
      style={{
        backgroundImage: `url(${siteBackground})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div className="absolute inset-0 bg-[#061A2C]/82" aria-hidden="true" />
      <div className="absolute -right-40 top-20 h-96 w-96 rounded-full bg-[#0D9488]/20 blur-3xl" aria-hidden="true" />
      <div className="absolute -left-40 bottom-0 h-96 w-96 rounded-full bg-cyan-400/10 blur-3xl" aria-hidden="true" />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-6 lg:px-10">
        <header className="flex items-center justify-between border-b border-white/10 pb-5">
          <Link to="/" className="flex items-center gap-3" aria-label="Credence AI home">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#0D9488] shadow-lg shadow-teal-950/30">
              <ShieldCheck className="h-5 w-5 text-white" />
            </span>
            <span className="text-sm font-black tracking-[0.18em]">CREDENCE <span className="text-[#5EEAD4]">AI</span></span>
          </Link>
          <Link
            to="/login"
            className="rounded-full border border-white/20 px-4 py-2 text-xs font-bold text-white/90 transition hover:border-[#5EEAD4] hover:bg-white/10 hover:text-white"
          >
            Sign in
          </Link>
        </header>

        <main className="flex flex-1 flex-col justify-center py-16 lg:py-20">
          <div className="grid items-center gap-14 lg:grid-cols-[1.08fr_0.92fr]">
            <section>
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#5EEAD4]/30 bg-[#0D9488]/15 px-3 py-1.5 text-[11px] font-bold uppercase tracking-[0.18em] text-[#99F6E4]">
                <Sparkles className="h-3.5 w-3.5" />
                Alternative credit intelligence
              </div>
              <h1 className="max-w-3xl text-4xl font-black leading-[1.05] tracking-tight text-white sm:text-5xl lg:text-7xl">
                Credit decisions that earn trust.
              </h1>
              <p className="mt-6 max-w-xl text-base leading-7 text-slate-200/85 sm:text-lg">
                Credence AI helps underwriting teams turn informal financial signals into clear, fair, and explainable decisions—without losing the human context behind every application.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  to="/login"
                  className="group inline-flex items-center justify-center gap-2 rounded-xl bg-[#0D9488] px-5 py-3.5 text-sm font-extrabold text-white shadow-xl shadow-teal-950/30 transition hover:-translate-y-0.5 hover:bg-[#14B8A6]"
                >
                  Open the underwriting portal
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
                <a
                  href="#capabilities"
                  className="inline-flex items-center justify-center rounded-xl border border-white/20 bg-white/5 px-5 py-3.5 text-sm font-bold text-white/90 backdrop-blur-sm transition hover:-translate-y-0.5 hover:bg-white/10"
                >
                  Explore the platform
                </a>
              </div>
              <div className="mt-10 flex flex-wrap gap-x-6 gap-y-3 text-xs font-semibold text-slate-300">
                <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-[#5EEAD4]" /> Explainable scores</span>
                <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-[#5EEAD4]" /> Fairness visibility</span>
                <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-[#5EEAD4]" /> Decision trail</span>
              </div>
            </section>

            <section aria-label="Credence AI product preview" className="relative">
              <div className="absolute -inset-4 rounded-[2rem] bg-cyan-300/10 blur-2xl" aria-hidden="true" />
              <div className="relative overflow-hidden rounded-[1.75rem] border border-white/20 bg-slate-950/60 p-5 shadow-2xl shadow-slate-950/50 backdrop-blur-xl sm:p-7">
                <div className="flex items-start justify-between border-b border-white/10 pb-5">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#5EEAD4]">Live decision cockpit</p>
                    <h2 className="mt-2 text-xl font-extrabold text-white">Application intelligence</h2>
                  </div>
                  <span className="rounded-full bg-emerald-400/15 px-2.5 py-1 text-[10px] font-bold text-emerald-300">Model online</span>
                </div>
                <div className="mt-6 grid grid-cols-2 gap-3">
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-[10px] font-semibold text-slate-400">Credence score</p>
                    <p className="mt-2 text-3xl font-black text-white">742</p>
                    <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/10"><div className="h-full w-[82%] rounded-full bg-gradient-to-r from-[#0D9488] to-[#5EEAD4]" /></div>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-[10px] font-semibold text-slate-400">Data confidence</p>
                    <p className="mt-2 text-3xl font-black text-[#99F6E4]">High</p>
                    <p className="mt-2 text-[10px] text-slate-400">Across 4 signal groups</p>
                  </div>
                </div>
                <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between text-xs font-bold text-white"><span>What shaped the decision?</span><span className="text-[#5EEAD4]">View factors</span></div>
                  <div className="mt-4 space-y-3">
                    {[["Stable cash flow", "78%", "w-[78%]"], ["Utility punctuality", "64%", "w-[64%]"], ["Month-end buffer", "52%", "w-[52%]"]].map(([label, value, width]) => (
                      <div key={label}>
                        <div className="mb-1 flex justify-between text-[10px] text-slate-300"><span>{label}</span><span>{value}</span></div>
                        <div className="h-1.5 rounded-full bg-white/10"><div className={`h-full rounded-full bg-[#2DD4BF] ${width}`} /></div>
                      </div>
                    ))}
                  </div>
                </div>
                <p className="mt-5 text-center text-[10px] font-medium text-slate-400">Designed for decisions people can understand.</p>
              </div>
            </section>
          </div>

          <section id="capabilities" className="mt-20 grid gap-4 border-t border-white/10 pt-8 md:grid-cols-3">
            {capabilities.map(({ icon: Icon, title, text }) => (
              <article key={title} className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm transition hover:-translate-y-1 hover:border-[#5EEAD4]/40 hover:bg-white/10">
                <Icon className="h-5 w-5 text-[#5EEAD4]" />
                <h3 className="mt-4 text-sm font-extrabold text-white">{title}</h3>
                <p className="mt-2 text-xs leading-5 text-slate-300">{text}</p>
              </article>
            ))}
          </section>
        </main>

        <footer className="flex flex-col gap-2 border-t border-white/10 py-5 text-[11px] text-slate-400 sm:flex-row sm:items-center sm:justify-between">
          <span>Credence AI · Secure underwriting intelligence</span>
          <span>Built for clearer decisions in the real economy.</span>
        </footer>
      </div>
    </div>
  );
};

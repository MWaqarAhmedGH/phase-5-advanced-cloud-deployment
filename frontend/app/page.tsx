import Link from "next/link";

export default function Home() {
  return (
    <div className="h-screen flex items-center justify-center relative overflow-hidden">
      {/* Aurora background orbs */}
      <div className="orb orb-emerald w-[450px] h-[450px] -top-24 -left-24" style={{ animationDelay: "0s" }}></div>
      <div className="orb orb-blue w-[350px] h-[350px] top-1/4 -right-16" style={{ animationDelay: "2.5s" }}></div>
      <div className="orb orb-violet w-[280px] h-[280px] bottom-16 left-1/4" style={{ animationDelay: "5s" }}></div>
      <div className="orb orb-amber w-[200px] h-[200px] top-2/3 right-1/4" style={{ animationDelay: "3.5s" }}></div>

      {/* Subtle grid */}
      <div className="absolute inset-0 bg-grid-3d opacity-40"></div>

      {/* Content */}
      <div className="relative z-10 text-center px-4 max-w-3xl mx-auto">
        {/* Glowing badge */}
        <div className="inline-flex items-center gap-2 badge-glow mb-8 animate-fade-in">
          <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
          Phase 5 &middot; Advanced Cloud Deployment
        </div>

        {/* Main heading with 3D effect */}
        <div className="perspective-container">
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 animate-slide-up tracking-tight">
            <span className="gradient-text-animated">AI Todo</span>
            <br />
            <span className="text-white drop-shadow-lg">Assistant</span>
          </h1>
        </div>

        {/* Subtitle */}
        <p className="text-lg md:text-xl text-slate-400 mb-4 max-w-lg mx-auto animate-slide-up leading-relaxed" style={{ animationDelay: "0.1s" }}>
          Manage tasks with natural language. Priorities, tags, reminders, recurring tasks &mdash; all through conversation.
        </p>

        {/* Feature pills */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-10 animate-slide-up" style={{ animationDelay: "0.15s" }}>
          {["Priorities", "Tags", "Due Dates", "Reminders", "Recurring", "Search & Filter"].map((feature) => (
            <span
              key={feature}
              className="px-3 py-1 text-xs font-medium text-emerald-300/80 bg-emerald-500/8 border border-emerald-500/15 rounded-full"
            >
              {feature}
            </span>
          ))}
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: "0.2s" }}>
          <Link
            href="/signin"
            className="btn-neon px-8 py-4 text-lg rounded-xl inline-flex items-center gap-2 group"
          >
            Get Started
            <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
          <Link
            href="/signup"
            className="btn-neon-outline px-8 py-4 text-lg rounded-xl"
          >
            Create Account
          </Link>
        </div>

        {/* Tech stack footer */}
        <div className="mt-16 animate-fade-in" style={{ animationDelay: "0.4s" }}>
          <p className="text-xs text-slate-500 mb-3 uppercase tracking-widest">Built with</p>
          <div className="flex items-center justify-center gap-4 text-xs text-slate-500">
            <span>Next.js</span>
            <span className="w-1 h-1 bg-slate-600 rounded-full"></span>
            <span>FastAPI</span>
            <span className="w-1 h-1 bg-slate-600 rounded-full"></span>
            <span>Dapr</span>
            <span className="w-1 h-1 bg-slate-600 rounded-full"></span>
            <span>Kafka</span>
            <span className="w-1 h-1 bg-slate-600 rounded-full"></span>
            <span>Kubernetes</span>
          </div>
        </div>
      </div>

      {/* Aurora line at bottom */}
      <div className="absolute bottom-0 left-0 right-0 aurora-line"></div>
    </div>
  );
}

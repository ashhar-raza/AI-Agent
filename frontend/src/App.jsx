import { useEffect, useRef, useState } from "react";

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

export default function App() {
  const [status, setStatus] = useState("Idle");
  const [transcript, setTranscript] = useState("");
  const [outcome, setOutcome] = useState(null);
  const [isCalling, setIsCalling] = useState(false);

  const recogRef = useRef(null);
  const speaking = useRef(false);
  const callActive = useRef(false);

  useEffect(() => {
    if (!SpeechRecognition) return;

    const recog = new SpeechRecognition();
    recog.continuous = true;
    recog.interimResults = true;
    recog.lang = "en-US";

    let silenceTimer = null;

    recog.onresult = (e) => {
      const r = e.results[e.results.length - 1];
      setTranscript(r[0].transcript);

      if (speaking.current) {
        window.speechSynthesis.cancel();
        speaking.current = false;
      }

      if (r.isFinal) {
        clearTimeout(silenceTimer);
        silenceTimer = setTimeout(() => {
          if (callActive.current) send(r[0].transcript);
        }, 600);
      }
    };

    recog.onend = () => {
      if (callActive.current) {
        try {
          recog.start();
        } catch {}
      } else {
        setStatus("Idle");
        setIsCalling(false);
      }
    };

    recogRef.current = recog;

    return () => {
      callActive.current = false;
      recog.stop();
    };
  }, []);

  const speak = (text) => {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.9;
    u.onstart = () => (speaking.current = true);
    u.onend = () => (speaking.current = false);
    window.speechSynthesis.speak(u);
  };

  const start = async () => {
    setOutcome(null);
    setStatus("Connecting");
    setIsCalling(true);
    callActive.current = true;

    try {
      recogRef.current.start();
      const r = await fetch("http://localhost:8000/start", { method: "POST" });
      const d = await r.json();
      speak(d.reply);
      setStatus("Listening");
    } catch {
      setStatus("Error");
      setIsCalling(false);
    }
  };

  const send = async (text) => {
    setStatus("Thinking");

    const r = await fetch("http://localhost:8000/next", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const d = await r.json();

    if (d.end) {
      callActive.current = false;
      recogRef.current.stop();
      setIsCalling(false);
      setOutcome(d.final);
      speak("Thanks for your time.");
      setStatus("Call Ended");
      return;
    }

    speak(d.reply);
    setStatus("Listening");
  };

  const statusStyles = {
    Idle: "text-gray-400",
    Connecting: "text-yellow-400 animate-pulse",
    Listening: "text-green-400 animate-pulse",
    Thinking: "text-blue-400 animate-pulse",
    "Call Ended": "text-purple-400",
  }[status];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-zinc-900 to-indigo-950 text-white">
      
      {/* Glow layer */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(99,102,241,0.15),_transparent_60%)]" />

      <div className="relative w-full max-w-xl rounded-2xl border border-zinc-800 bg-zinc-950/90 p-8 shadow-[0_0_60px_rgba(99,102,241,0.25)] backdrop-blur">

        {/* Header */}
        <div className="mb-6 flex items-center gap-3">
          <span className="text-3xl">📞</span>
          <h1 className="text-2xl font-bold tracking-wide">
            AI Cold Caller
          </h1>
        </div>

        {/* Call Button */}
        <button
          onClick={start}
          disabled={isCalling}
          className={`w-full py-3 rounded-xl text-lg font-semibold transition-all
            ${
              isCalling
                ? "bg-zinc-700 cursor-not-allowed"
                : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-lg"
            }`}
        >
          {isCalling ? "Call in Progress…" : "Start Call"}
        </button>

        {/* Status */}
        <div className="mt-6 text-sm">
          <span className="text-gray-500">Status:</span>{" "}
          <span className={`font-medium ${statusStyles}`}>
            {status}
          </span>
        </div>

        {/* Transcript */}
        {transcript && (
          <div className="mt-4 rounded-lg border border-zinc-800 bg-black/70 p-4 text-sm text-gray-200">
            <span className="text-gray-500">You said:</span>{" "}
            {transcript}
          </div>
        )}

        {/* Outcome */}
        {outcome && (
          <div className="mt-6 rounded-xl border border-green-700/50 bg-gradient-to-br from-zinc-900 to-zinc-800 p-5 shadow-inner">
            <div className="mb-2 flex items-center gap-2 text-green-400 font-semibold">
              ✅ Outcome
            </div>
            <pre className="text-sm text-gray-200 whitespace-pre-wrap">
              {outcome}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

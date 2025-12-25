import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Loader2, Upload, Copy, Download, AlertCircle, CheckCircle, Shield, Lock, Eye, Zap, Settings, GitCompare, FileCode, Terminal, Activity, Cpu } from "lucide-react";
import { toast } from "sonner";
import { CodeDiffView } from "@/components/CodeDiffView";
import { motion, AnimatePresence } from "framer-motion";

interface AnalysisResult {
  status: string;
  report: {
    success: boolean;
    detected: boolean;
    ml_confidence: number;
    vulnerability_type: string;
    patch_score: number;
    patched_code: string;
    validated: boolean;
  };
}

export default function Home() {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [apiUrl, setApiUrl] = useState("https://acrs-autonomous-cyber-reasoning-system.onrender.com");
  const [showApiConfig, setShowApiConfig] = useState(false);
  const [showDiffView, setShowDiffView] = useState(true);

  // Check API status on mount
  useEffect(() => {
    checkApiStatus();
  }, [apiUrl]);

  const checkApiStatus = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/status`);
      if (!response.ok) {
        setError("System offline. Backend connection failed.");
      } else {
        setError(null);
      }
    } catch (err) {
      setError("Connection refused. Verify neural link (API URL).");
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCode(e.target?.result as string);
        setError(null);
      };
      reader.onerror = () => {
        setError("Data packet corrupted. Read failed.");
      };
      reader.readAsText(file);
    }
  };

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError("Input buffer empty. Initiate data stream.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Analysis sequence terminated.");
      }

      const data = await response.json();
      setResult(data);
      toast.success("Analysis sequence complete.");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Fatal system error";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = () => {
    if (result?.report.patched_code) {
      navigator.clipboard.writeText(result.report.patched_code);
      toast.success("Code extracted to clipboard.");
    }
  };

  const handleDownloadCode = () => {
    if (result?.report.patched_code) {
      const element = document.createElement("a");
      const file = new Blob([result.report.patched_code], { type: "text/plain" });
      element.href = URL.createObjectURL(file);
      element.download = "patched_source.py";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      toast.success("Source file downloaded.");
    }
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 100 } }
  };

  return (
    <div className="min-h-screen relative text-blue-50 font-sans selection:bg-cyan-500/30 selection:text-cyan-100">
      {/* Background Decor */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-[#050510] to-slate-950"></div>
        <div className="scanline"></div>
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-950/0 to-slate-950/0"></div>
      </div>

      {/* Header HUD */}
      <header className="sticky top-0 z-50 border-b border-cyan-500/20 bg-slate-950/80 backdrop-blur-md">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg blur opacity-40 group-hover:opacity-75 transition duration-200"></div>
                <div className="relative w-12 h-12 bg-slate-900 rounded-lg border border-cyan-500/50 flex items-center justify-center">
                  <Shield className="w-6 h-6 text-cyan-400" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 font-mono">
                  ACRS<span className="text-xs ml-2 text-blue-500 font-normal tracking-widest">v1.0.0</span>
                </h1>
                <p className="text-xs text-blue-400/60 uppercase tracking-widest font-mono">Autonomous Cyber Reasoning System</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/30 border border-blue-500/20">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs text-blue-300 font-mono">SYSTEM ONLINE</span>
              </div>
              <button
                onClick={() => setShowApiConfig(!showApiConfig)}
                className="text-xs font-mono text-cyan-500 hover:text-cyan-300 transition-colors flex items-center gap-2 border border-cyan-500/30 px-3 py-2 rounded bg-cyan-950/20 hover:bg-cyan-900/40"
              >
                <Settings className="w-3 h-3" />
                {showApiConfig ? "HIDE CONFIG" : "CONFIG"}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-4 py-8 md:py-12">
        <motion.div 
          initial="hidden"
          animate="visible"
          variants={containerVariants}
        >
          {/* Hero Section */}
          <motion.div variants={itemVariants} className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-blue-500/30 bg-blue-500/5 mb-6">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span className="text-sm text-cyan-300 font-mono">NEURAL ENGINE READY</span>
            </div>
            <h1 className="text-4xl md:text-7xl font-bold mb-6 tracking-tight">
              <span className="text-white text-glow-blue">Secure Your </span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 text-glow-cyan">Infrastructure</span>
            </h1>
            <p className="text-lg text-blue-200/60 max-w-2xl mx-auto font-light">
              Advanced AI heuristics for vulnerability detection and automated patch synthesis.
            </p>
          </motion.div>

          {/* API Configuration Panel */}
          <AnimatePresence>
            {showApiConfig && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden mb-6"
              >
                <div className="p-4 border border-cyan-500/30 bg-slate-900/90 backdrop-blur rounded-lg">
                  <div className="flex gap-2 max-w-xl mx-auto">
                    <div className="relative flex-1">
                      <Terminal className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                      <input
                        type="text"
                        value={apiUrl}
                        onChange={(e) => setApiUrl(e.target.value)}
                        placeholder="http://localhost:5000"
                        className="w-full pl-10 pr-4 py-2 border border-slate-700 rounded bg-slate-950 text-cyan-300 font-mono text-sm focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all"
                      />
                    </div>
                    <Button 
                      onClick={checkApiStatus} 
                      className="bg-cyan-600 hover:bg-cyan-500 text-white border border-cyan-400/50"
                      size="sm"
                    >
                      PING
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error Alert */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                className="mb-8 max-w-4xl mx-auto"
              >
                <div className="p-4 border-l-4 border-red-500 bg-red-950/20 backdrop-blur-sm flex gap-4 items-center shadow-[0_0_20px_rgba(239,68,68,0.2)]">
                  <AlertCircle className="text-red-500 w-6 h-6 animate-pulse" />
                  <div>
                    <p className="text-xs font-mono text-red-400 uppercase tracking-wider">System Critical</p>
                    <p className="text-red-200">{error}</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-7xl mx-auto">
            {/* Input Section */}
            <motion.div variants={itemVariants} className="h-full">
              <div className="tech-card h-full rounded-xl p-1">
                <div className="bg-slate-950/50 p-6 h-full rounded-lg flex flex-col">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-white flex items-center gap-3">
                      <div className="p-2 bg-blue-500/10 rounded border border-blue-500/20">
                        <Terminal className="w-5 h-5 text-blue-400" />
                      </div>
                      Source Input
                    </h2>
                    <div className="flex gap-2">
                       <label className="cursor-pointer group">
                        <input type="file" accept=".py" onChange={handleFileUpload} className="hidden" />
                        <div className="px-3 py-1.5 rounded border border-blue-500/30 bg-blue-500/5 text-blue-300 text-xs font-mono uppercase hover:bg-blue-500/20 transition-all flex items-center gap-2">
                          <Upload className="w-3 h-3 group-hover:-translate-y-0.5 transition-transform" />
                          Load File
                        </div>
                      </label>
                    </div>
                  </div>
                  
                  <div className="flex-1 relative group">
                    <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-transparent pointer-events-none rounded-lg"></div>
                    <textarea
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      placeholder="# Initiate input sequence..."
                      className="w-full h-[400px] lg:h-[500px] p-4 bg-slate-900/80 border border-slate-800 rounded-lg text-blue-100 font-mono text-sm focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all resize-none leading-relaxed custom-scrollbar"
                      spellCheck="false"
                    />
                  </div>

                  <div className="mt-6">
                    <Button
                      onClick={handleAnalyze}
                      disabled={loading || !code.trim()}
                      className="w-full h-12 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold tracking-widest relative overflow-hidden group border-0"
                    >
                      <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                      {loading ? (
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-5 h-5 animate-spin" />
                          <span>PROCESSING NEURAL NET...</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Zap className="w-5 h-5 fill-current" />
                          <span>INITIATE ANALYSIS</span>
                        </div>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Results Section */}
            <motion.div variants={itemVariants} className="space-y-6">
              <AnimatePresence mode="wait">
                {result ? (
                  <motion.div 
                    key="results"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-6"
                  >
                    {/* Status Card */}
                    <div className={`tech-card rounded-xl p-6 border-l-4 ${result.report.detected ? 'border-l-red-500 border-red-500/30' : 'border-l-green-500 border-green-500/30'}`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`p-3 rounded-full border-2 ${result.report.detected ? 'border-red-500 bg-red-500/20 animate-pulse' : 'border-green-500 bg-green-500/20'}`}>
                            {result.report.detected ? (
                              <AlertCircle className="w-8 h-8 text-red-400" />
                            ) : (
                              <CheckCircle className="w-8 h-8 text-green-400" />
                            )}
                          </div>
                          <div>
                            <h3 className="text-2xl font-bold text-white tracking-wide">
                              {result.report.detected ? "THREAT DETECTED" : "SYSTEM SECURE"}
                            </h3>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="w-2 h-2 bg-current rounded-full animate-ping"></span>
                              <p className={`text-sm font-mono tracking-widest ${result.report.detected ? 'text-red-400' : 'text-green-400'}`}>
                                {result.report.detected ? "CRITICAL VULNERABILITY FOUND" : "NO ANOMALIES DETECTED"}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="text-right hidden sm:block">
                          <p className="text-xs text-slate-400 font-mono uppercase">Confidence</p>
                          <p className="text-3xl font-bold font-mono text-white">
                            {(result.report.ml_confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Diagnostics */}
                    <div className="tech-card rounded-xl p-1">
                      <div className="bg-slate-950/50 p-6 rounded-lg">
                        <h3 className="font-mono text-cyan-400 text-sm uppercase tracking-widest mb-6 border-b border-cyan-500/20 pb-2 flex items-center gap-2">
                          <Activity className="w-4 h-4" />
                          Diagnostic Telemetry
                        </h3>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-4 bg-slate-900/50 rounded border border-slate-800">
                            <p className="text-xs text-slate-500 font-mono mb-1">Safety Rating</p>
                            <div className="flex items-end gap-2">
                              <span className={`text-2xl font-mono font-bold ${result.report.detected ? 'text-red-400' : 'text-green-400'}`}>
                                {result.report.detected 
                                  ? ((1.0 - result.report.ml_confidence) * 100).toFixed(1)
                                  : (result.report.ml_confidence * 100).toFixed(1)}
                              </span>
                              <span className="text-xs text-slate-500 mb-1">/ 100</span>
                            </div>
                            <div className="w-full bg-slate-800 h-1 mt-2 rounded-full overflow-hidden">
                              <div 
                                className={`h-full ${result.report.detected ? 'bg-red-500' : 'bg-green-500'}`} 
                                style={{ width: `${result.report.detected ? (1.0 - result.report.ml_confidence) * 100 : result.report.ml_confidence * 100}%` }}
                              ></div>
                            </div>
                          </div>

                          {result.report.detected && (
                            <div className="p-4 bg-slate-900/50 rounded border border-slate-800">
                              <p className="text-xs text-slate-500 font-mono mb-1">Threat Signature</p>
                              <span className="text-lg font-semibold text-red-300 block truncate">
                                {result.report.vulnerability_type}
                              </span>
                            </div>
                          )}

                          {result.report.detected && (
                            <>
                              <div className="p-4 bg-slate-900/50 rounded border border-slate-800">
                                <p className="text-xs text-slate-500 font-mono mb-1">Patch Integrity</p>
                                <span className="text-2xl font-mono font-bold text-white">
                                  {result.report.patch_score.toFixed(2)}
                                </span>
                              </div>
                              <div className="p-4 bg-slate-900/50 rounded border border-slate-800">
                                <p className="text-xs text-slate-500 font-mono mb-1">Validation</p>
                                <span className={`text-lg font-bold font-mono ${result.report.validated ? 'text-green-400' : 'text-yellow-400'}`}>
                                  {result.report.validated ? "VERIFIED" : "PENDING"}
                                </span>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div 
                    key="placeholder"
                    initial={{ opacity: 0 }} 
                    animate={{ opacity: 1 }}
                    className="h-full flex items-center justify-center p-12 tech-card rounded-xl border-dashed border-slate-800 bg-slate-950/30"
                  >
                    <div className="text-center opacity-40">
                      <Activity className="w-16 h-16 mx-auto mb-4 text-cyan-900 animate-pulse" />
                      <p className="font-mono text-cyan-700">AWAITING INPUT DATA STREAM...</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>

          {/* Patched Code Section */}
          <AnimatePresence>
            {result && result.report.detected && result.report.patched_code && (
              <motion.div 
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mt-12"
              >
                <div className="flex flex-col md:flex-row items-center justify-between mb-6 gap-4">
                  <h3 className="text-xl font-bold text-white flex items-center gap-3">
                    <div className="p-2 bg-purple-500/10 rounded border border-purple-500/20">
                      <Lock className="w-5 h-5 text-purple-400" />
                    </div>
                    Remediation Protocol
                  </h3>
                  
                  <div className="flex p-1 bg-slate-900 rounded-lg border border-slate-700">
                    <button
                      onClick={() => setShowDiffView(true)}
                      className={`px-4 py-2 rounded text-xs font-mono transition-all ${showDiffView ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20' : 'text-slate-400 hover:text-white'}`}
                    >
                      <GitCompare className="w-3 h-3 inline mr-2" />
                      DIFF VIEW
                    </button>
                    <button
                      onClick={() => setShowDiffView(false)}
                      className={`px-4 py-2 rounded text-xs font-mono transition-all ${!showDiffView ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20' : 'text-slate-400 hover:text-white'}`}
                    >
                      <FileCode className="w-3 h-3 inline mr-2" />
                      RAW SOURCE
                    </button>
                  </div>
                </div>

                <div className="tech-card rounded-xl overflow-hidden">
                  <div className="border-b border-slate-800 bg-slate-950 px-4 py-2 flex items-center justify-between">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
                      <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                      <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleCopyCode} variant="ghost" size="sm" className="h-8 text-xs text-slate-400 hover:text-cyan-400 hover:bg-cyan-950/30">
                        <Copy className="w-3 h-3 mr-2" /> COPY
                      </Button>
                      <Button onClick={handleDownloadCode} variant="ghost" size="sm" className="h-8 text-xs text-slate-400 hover:text-cyan-400 hover:bg-cyan-950/30">
                        <Download className="w-3 h-3 mr-2" /> EXPORT
                      </Button>
                    </div>
                  </div>
                  
                  <div className="bg-slate-950 p-1">
                    {showDiffView ? (
                      <div className="rounded overflow-hidden border border-slate-800">
                        <CodeDiffView originalCode={code} patchedCode={result.report.patched_code} />
                      </div>
                    ) : (
                      <pre className="p-6 bg-slate-900/50 text-blue-100 overflow-x-auto text-sm font-mono custom-scrollbar max-h-[600px]">
                        <code>{result.report.patched_code}</code>
                      </pre>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Feature Grid */}
          {!result && (
            <motion.div 
              variants={containerVariants}
              className="mt-20 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
              {[
                { icon: Shield, title: "Heuristic Scans", desc: "Deep learning algorithms detect logic flaws." },
                { icon: Lock, title: "Auto-Patching", desc: "Generates secure code replacements instantly." },
                { icon: Eye, title: "Transparent Ops", desc: "Full visibility into confidence and logic." },
                { icon: Zap, title: "Real-time Core", desc: "Zero-latency processing pipeline." }
              ].map((feature, index) => (
                <motion.div 
                  key={index}
                  variants={itemVariants}
                  className="group relative p-6 bg-slate-900/40 border border-slate-800 hover:border-cyan-500/50 rounded-xl transition-all hover:shadow-[0_0_30px_rgba(6,182,212,0.1)] overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <div className="relative z-10">
                    <feature.icon className="w-8 h-8 text-slate-600 group-hover:text-cyan-400 mb-4 transition-colors" />
                    <h4 className="text-white font-bold mb-2 group-hover:text-cyan-200 transition-colors">{feature.title}</h4>
                    <p className="text-sm text-slate-500 group-hover:text-slate-400">{feature.desc}</p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </motion.div>
      </main>
    </div>
  );
}
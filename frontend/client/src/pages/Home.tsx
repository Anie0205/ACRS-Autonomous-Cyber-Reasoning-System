import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Loader2, Upload, Copy, Download, AlertCircle, CheckCircle, Shield, Lock, Eye, Zap, Settings, GitCompare, FileCode } from "lucide-react";
import { APP_LOGO, APP_TITLE } from "@/const";
import { toast } from "sonner";
import { CodeDiffView } from "@/components/CodeDiffView";

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
        setError("API is not available. Please ensure the backend is running.");
      } else {
        setError(null);
      }
    } catch (err) {
      setError("Cannot connect to API. Check the API URL and ensure the backend is running.");
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
        setError("Failed to read file");
      };
      reader.readAsText(file);
    }
  };

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError("Please enter or upload Python code");
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
        throw new Error(errorData.error || "Analysis failed");
      }

      const data = await response.json();
      setResult(data);
      toast.success("Analysis completed successfully!");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An error occurred during analysis";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = () => {
    if (result?.report.patched_code) {
      navigator.clipboard.writeText(result.report.patched_code);
      toast.success("Patched code copied to clipboard!");
    }
  };

  const handleDownloadCode = () => {
    if (result?.report.patched_code) {
      const element = document.createElement("a");
      const file = new Blob([result.report.patched_code], { type: "text/plain" });
      element.href = URL.createObjectURL(file);
      element.download = "patched_code.py";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      toast.success("Patched code downloaded!");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white relative overflow-hidden">
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-blue-400/5 rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-blue-500/20 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/50">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">ACRS</h1>
                <p className="text-sm text-blue-300/80">Autonomous Cyber Reasoning System</p>
              </div>
            </div>
            <button
              onClick={() => setShowApiConfig(!showApiConfig)}
              className="text-sm text-blue-300 hover:text-blue-200 transition-colors flex items-center gap-2"
            >
              <Settings className="w-4 h-4" />
              {showApiConfig ? "Hide" : "Configure"} API
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-white via-blue-200 to-blue-400 bg-clip-text text-transparent">
            Unleashing the Power of <span className="text-blue-400">Cyber Security</span>
          </h1>
          <p className="text-xl text-blue-200/80 max-w-2xl mx-auto">
            Transforming code security with AI-powered vulnerability detection and automated patching
          </p>
        </div>

        {/* API Configuration */}
        {showApiConfig && (
          <Card className="mb-6 p-4 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10">
            <div className="flex gap-2">
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:5000"
                className="flex-1 px-4 py-2 border border-blue-500/30 rounded-lg bg-slate-900/50 text-white placeholder:text-blue-300/50 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              />
              <Button 
                onClick={checkApiStatus} 
                className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-500/30"
                size="sm"
              >
                Test Connection
              </Button>
            </div>
          </Card>
        )}

        {/* Error Alert */}
        {error && (
          <Card className="mb-6 p-4 border-red-500/30 bg-red-950/30 backdrop-blur-sm flex gap-3 shadow-lg shadow-red-500/10">
            <AlertCircle className="text-red-400 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-300">Error</p>
              <p className="text-sm text-red-200/80">{error}</p>
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="space-y-4">
            <Card className="p-6 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-blue-400" />
                Python Code Analysis
              </h2>
              <div className="space-y-3">
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="Paste your Python code here or upload a file..."
                  className="w-full h-64 p-4 border border-blue-500/30 rounded-lg bg-slate-900/50 text-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-blue-300/50 backdrop-blur-sm"
                />
                <div className="flex gap-2">
                  <label className="flex-1">
                    <input
                      type="file"
                      accept=".py"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      className="w-full cursor-pointer border-blue-500/30 bg-slate-800/50 text-white hover:bg-slate-700/50 hover:border-blue-500/50"
                      onClick={(e) => {
                        e.preventDefault();
                        const input = e.currentTarget.parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
                        input?.click();
                      }}
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Upload File
                    </Button>
                  </label>
                  <Button
                    onClick={handleAnalyze}
                    disabled={loading || !code.trim()}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white shadow-lg shadow-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      "Analyze Code"
                    )}
                  </Button>
                </div>
              </div>
            </Card>
          </div>

          {/* Results Section */}
          <div className="space-y-4">
            {result ? (
              <>
                {/* Report Summary */}
                <Card className="p-6 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10">
                  <div className="flex items-start gap-3 mb-4">
                    {result.report.detected ? (
                      <div className="p-2 bg-red-500/20 rounded-lg border border-red-500/30">
                        <AlertCircle className="text-red-400 flex-shrink-0" />
                      </div>
                    ) : (
                      <div className="p-2 bg-green-500/20 rounded-lg border border-green-500/30">
                        <CheckCircle className="text-green-400 flex-shrink-0" />
                      </div>
                    )}
                    <div>
                      <h3 className="font-semibold text-white text-lg">
                        {result.report.detected ? "Vulnerability Detected" : "Code is Safe"}
                      </h3>
                      <p className="text-sm text-blue-300/80 mt-1">
                        Status: <span className={`font-semibold ${result.report.detected ? 'text-red-400' : 'text-green-400'}`}>
                          {result.report.detected ? "VULNERABLE" : "SAFE"}
                        </span>
                      </p>
                    </div>
                  </div>
                </Card>

                {/* Analysis Details */}
                <Card className="p-6 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10">
                  <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                    <Eye className="w-5 h-5 text-blue-400" />
                    Analysis Details
                  </h3>
                  <div className="space-y-3">
                    <div className="p-4 bg-slate-900/50 rounded-lg border border-blue-500/20">
                      <div className="text-sm space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-blue-300/80">ML Confidence:</span>
                          <span className="font-mono font-semibold text-white text-lg">
                            {(result.report.ml_confidence * 100).toFixed(2)}%
                          </span>
                        </div>
                        <div className="h-px bg-blue-500/20"></div>
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-blue-300/80">Safety Score:</span>
                          <span className="font-mono font-semibold text-green-400 text-lg">
                            {result.report.detected 
                              ? ((1.0 - result.report.ml_confidence) * 100).toFixed(2) + "%"
                              : (result.report.ml_confidence * 100).toFixed(2) + "%"}
                          </span>
                        </div>
                        {result.report.detected && (
                          <>
                            <div className="h-px bg-blue-500/20"></div>
                            <div className="flex justify-between items-center">
                              <span className="font-medium text-blue-300/80">Vulnerability Type:</span>
                              <span className="font-semibold text-red-400">
                                {result.report.vulnerability_type}
                              </span>
                            </div>
                            <div className="h-px bg-blue-500/20"></div>
                            <div className="flex justify-between items-center">
                              <span className="font-medium text-blue-300/80">Patch Score:</span>
                              <span className="font-mono font-semibold text-white">
                                {result.report.patch_score.toFixed(2)} / 1.0
                              </span>
                            </div>
                            <div className="h-px bg-blue-500/20"></div>
                            <div className="flex justify-between items-center">
                              <span className="font-medium text-blue-300/80">Validated:</span>
                              <span className={`font-semibold ${result.report.validated ? 'text-green-400' : 'text-yellow-400'}`}>
                                {result.report.validated ? "YES" : "NO"}
                              </span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              </>
            ) : (
              <Card className="p-6 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10 text-center">
                <p className="text-blue-300/60">Submit code to see analysis results</p>
              </Card>
            )}
          </div>
        </div>

        {/* Patched Code Section */}
        {result && result.report.detected && result.report.patched_code && (
          <div className="mt-8">
            {/* View Toggle */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Lock className="w-5 h-5 text-blue-400" />
                Code Changes
              </h3>
              <div className="flex gap-2">
                <Button
                  onClick={() => setShowDiffView(true)}
                  variant={showDiffView ? "default" : "outline"}
                  size="sm"
                  className={`gap-2 ${
                    showDiffView
                      ? "bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-500/30"
                      : "border-blue-500/30 bg-slate-800/50 text-white hover:bg-slate-700/50 hover:border-blue-500/50"
                  }`}
                >
                  <GitCompare className="w-4 h-4" />
                  Diff View
                </Button>
                <Button
                  onClick={() => setShowDiffView(false)}
                  variant={!showDiffView ? "default" : "outline"}
                  size="sm"
                  className={`gap-2 ${
                    !showDiffView
                      ? "bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-500/30"
                      : "border-blue-500/30 bg-slate-800/50 text-white hover:bg-slate-700/50 hover:border-blue-500/50"
                  }`}
                >
                  <FileCode className="w-4 h-4" />
                  Patched Code
                </Button>
                <Button
                  onClick={handleCopyCode}
                  variant="outline"
                  size="sm"
                  className="gap-2 border-blue-500/30 bg-slate-800/50 text-white hover:bg-slate-700/50 hover:border-blue-500/50"
                >
                  <Copy className="w-4 h-4" />
                  Copy
                </Button>
                <Button
                  onClick={handleDownloadCode}
                  variant="outline"
                  size="sm"
                  className="gap-2 border-blue-500/30 bg-slate-800/50 text-white hover:bg-slate-700/50 hover:border-blue-500/50"
                >
                  <Download className="w-4 h-4" />
                  Download
                </Button>
              </div>
            </div>

            {/* Diff View or Patched Code View */}
            {showDiffView ? (
              <CodeDiffView originalCode={code} patchedCode={result.report.patched_code} />
            ) : (
              <Card className="border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10">
                <div className="p-4 border-b border-blue-500/20 bg-slate-900/50">
                  <div className="flex items-center gap-2">
                    <FileCode className="w-5 h-5 text-blue-400" />
                    <h4 className="text-lg font-semibold text-white">Patched Code</h4>
                  </div>
                </div>
                <pre className="p-4 bg-slate-900/80 text-blue-100 overflow-x-auto text-sm font-mono border border-blue-500/20 shadow-inner max-h-[600px] overflow-y-auto">
                  <code>{result.report.patched_code}</code>
                </pre>
              </Card>
            )}
          </div>
        )}
        {result && !result.report.detected && (
          <Card className="mt-8 p-6 border-green-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-green-500/10">
            <div className="text-center py-4">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-green-500/30">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
              <p className="text-green-300/90 text-lg">
                No vulnerabilities detected. Your code appears to be safe.
              </p>
            </div>
          </Card>
        )}

        {/* Feature Cards Section */}
        {!result && (
          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20 transition-all">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4 border border-blue-500/30">
                <Shield className="w-6 h-6 text-blue-400" />
              </div>
              <h4 className="font-semibold text-white mb-2">AI-Powered Detection</h4>
              <p className="text-sm text-blue-300/70">Advanced ML models identify vulnerabilities with high accuracy</p>
            </Card>
            <Card className="p-6 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20 transition-all">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4 border border-blue-500/30">
                <Lock className="w-6 h-6 text-blue-400" />
              </div>
              <h4 className="font-semibold text-white mb-2">Automated Patching</h4>
              <p className="text-sm text-blue-300/70">Intelligent code transformation to fix security issues</p>
            </Card>
            <Card className="p-6 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20 transition-all">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4 border border-blue-500/30">
                <Eye className="w-6 h-6 text-blue-400" />
              </div>
              <h4 className="font-semibold text-white mb-2">Transparent Analysis</h4>
              <p className="text-sm text-blue-300/70">Detailed reports with confidence scores and findings</p>
            </Card>
            <Card className="p-6 border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20 transition-all">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4 border border-blue-500/30">
                <Zap className="w-6 h-6 text-blue-400" />
              </div>
              <h4 className="font-semibold text-white mb-2">Fast Processing</h4>
              <p className="text-sm text-blue-300/70">Real-time analysis with instant results</p>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}

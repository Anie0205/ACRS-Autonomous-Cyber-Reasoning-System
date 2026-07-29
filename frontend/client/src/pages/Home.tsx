import React, { useState } from 'react';
import CodeDiffView from '../components/CodeDiffView';

interface AnalyzeResult {
  explanation: string;
  fix_summary: string;
  patched_code: string;
}

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
}

declare global {
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
  
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}

export default function Home() {
  const [code, setCode] = useState<string>('user_input = input()\neval(user_input)');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const backendUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${backendUrl}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        let message = `Server returned status ${response.status}`;
        try {
          const errBody = await response.json();
          if (errBody?.error || errBody?.message) {
            message = errBody.error || errBody.message;
          }
        } catch {
          // response wasn't JSON, keep default message
        }
        throw new Error(message);
      }

      const data: AnalyzeResult = await response.json();
      setResult(data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Failed to connect to backend server.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <header className="border-b border-gray-800 pb-4">
          <h1 className="text-3xl font-extrabold text-blue-400">
            Autonomous Cyber Reasoning System (ACRS)
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            AST Taint Analysis Engine &amp; Gemini Autonomous Security Remediation
          </p>
        </header>

        <div className="space-y-2">
          <label htmlFor="source-code" className="block text-sm font-medium text-gray-300">
            Python Source Code
          </label>
          <textarea
            id="source-code"
            value={code}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCode(e.target.value)}
            rows={8}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg p-4 font-mono text-sm text-green-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Paste Python code here..."
          />
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading || !code.trim()}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Analyzing AST & Querying Gemini...' : 'Analyze & Autonomously Patch'}
        </button>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg">
            ⚠️ Error: {error}
          </div>
        )}

        {result && <CodeDiffView result={result} />}
      </div>
    </div>
  );
}
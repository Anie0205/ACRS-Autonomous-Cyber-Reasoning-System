import React from 'react';

interface CodeDiffViewProps {
  result: {
    status: string;
    vulnerabilities: any[];
    patch: {
      explanation: string;
      fix_summary: string;
      patched_code: string;
    } | null;
  } | null;
}

export const CodeDiffView: React.FC<CodeDiffViewProps> = ({ result }) => {
  if (!result) return <div className="p-4 text-gray-500">Submit code to see analysis.</div>;

  if (result.status === 'safe') {
    return (
      <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
        <h3 className="text-green-700 font-bold">✅ Code is Secure</h3>
        <p className="text-green-600 text-sm">No AST taint vulnerabilities detected.</p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
        <h3 className="text-red-700 font-bold">🚨 Vulnerability Detected</h3>
        <p className="text-red-600 text-sm">
          Detected <strong>{result.vulnerabilities[0]?.cwe}</strong> involving the sink 
          <code> {result.vulnerabilities[0]?.sink}</code>.
        </p>
      </div>

      {result.patch && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
          <h3 className="text-blue-800 font-bold mb-2">🤖 Gemini Autonomous Patch</h3>
          <p className="text-blue-900 text-sm mb-2"><strong>Risk:</strong> {result.patch.explanation}</p>
          <p className="text-blue-900 text-sm mb-4"><strong>Fix:</strong> {result.patch.fix_summary}</p>
          
          <div className="bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
            <pre><code>{result.patch.patched_code}</code></pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeDiffView;

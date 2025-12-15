import { useMemo, useRef, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { GitCompare, X, Plus } from "lucide-react";

interface DiffLine {
  type: "added" | "removed" | "unchanged";
  content: string;
  lineNumber?: number;
}

interface CodeDiffViewProps {
  originalCode: string;
  patchedCode: string;
}

export function CodeDiffView({ originalCode, patchedCode }: CodeDiffViewProps) {
  const diff = useMemo(() => {
    return computeDiff(originalCode, patchedCode);
  }, [originalCode, patchedCode]);

  const originalScrollRef = useRef<HTMLDivElement>(null);
  const patchedScrollRef = useRef<HTMLDivElement>(null);
  const isScrollingRef = useRef(false);

  // Synchronized scrolling
  useEffect(() => {
    const originalEl = originalScrollRef.current;
    const patchedEl = patchedScrollRef.current;

    if (!originalEl || !patchedEl) return;

    const handleOriginalScroll = () => {
      if (!isScrollingRef.current && patchedEl) {
        isScrollingRef.current = true;
        patchedEl.scrollTop = originalEl.scrollTop;
        patchedEl.scrollLeft = originalEl.scrollLeft;
        setTimeout(() => {
          isScrollingRef.current = false;
        }, 50);
      }
    };

    const handlePatchedScroll = () => {
      if (!isScrollingRef.current && originalEl) {
        isScrollingRef.current = true;
        originalEl.scrollTop = patchedEl.scrollTop;
        originalEl.scrollLeft = patchedEl.scrollLeft;
        setTimeout(() => {
          isScrollingRef.current = false;
        }, 50);
      }
    };

    originalEl.addEventListener("scroll", handleOriginalScroll);
    patchedEl.addEventListener("scroll", handlePatchedScroll);

    return () => {
      originalEl.removeEventListener("scroll", handleOriginalScroll);
      patchedEl.removeEventListener("scroll", handlePatchedScroll);
    };
  }, [diff]);

  const stats = useMemo(() => {
    const removed = diff.original.filter((l) => l.type === "removed").length;
    const added = diff.patched.filter((l) => l.type === "added").length;
    const unchanged = diff.original.filter((l) => l.type === "unchanged").length;
    return { removed, added, unchanged };
  }, [diff]);

  return (
    <Card className="border-blue-500/30 bg-slate-800/50 backdrop-blur-sm shadow-lg shadow-blue-500/10 flex flex-col">
      <div className="p-4 border-b border-blue-500/20 bg-slate-900/50 flex-shrink-0">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <GitCompare className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Code Comparison</h3>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-blue-300/60">Changes:</span>
              {stats.removed > 0 && (
                <span className="text-red-300 font-semibold">-{stats.removed}</span>
              )}
              {stats.added > 0 && (
                <span className="text-green-300 font-semibold">+{stats.added}</span>
              )}
              {stats.unchanged > 0 && (
                <span className="text-blue-300/60">{stats.unchanged} unchanged</span>
              )}
            </div>
            <div className="flex gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-red-500/50 border border-red-500"></div>
                <span className="text-red-300/80">Removed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-green-500/50 border border-green-500"></div>
                <span className="text-green-300/80">Added</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-blue-500/30 border border-blue-500/50"></div>
                <span className="text-blue-300/80">Unchanged</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 divide-x divide-blue-500/20 h-[600px] min-h-0">
        {/* Original Code */}
        <div className="relative flex flex-col h-full min-h-0">
          <div className="sticky top-0 z-10 bg-slate-900/80 backdrop-blur-sm border-b border-blue-500/20 px-4 py-2 flex-shrink-0">
            <div className="flex items-center gap-2">
              <X className="w-4 h-4 text-red-400" />
              <span className="text-sm font-semibold text-red-300">Original Code</span>
            </div>
          </div>
          <div 
            ref={originalScrollRef}
            className="font-mono text-sm overflow-y-auto overflow-x-auto flex-1 min-h-0"
            style={{ maxHeight: '100%' }}
          >
            {diff.original.map((line, idx) => (
              <div
                key={`orig-${idx}`}
                className={`px-4 py-1 flex items-start gap-4 ${
                  line.type === "removed"
                    ? "bg-red-500/10 border-l-2 border-red-500"
                    : line.type === "unchanged"
                    ? "bg-slate-900/30"
                    : "bg-slate-900/50"
                }`}
              >
                <span className="text-blue-400/50 text-xs select-none min-w-[3rem] text-right">
                  {line.lineNumber || ""}
                </span>
                <span
                  className={`flex-1 whitespace-pre ${
                    line.type === "removed"
                      ? "text-red-300/80"
                      : line.type === "unchanged"
                      ? "text-blue-200/70"
                      : "text-slate-500/50"
                  }`}
                >
                  {line.content || " "}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Patched Code */}
        <div className="relative flex flex-col h-full min-h-0">
          <div className="sticky top-0 z-10 bg-slate-900/80 backdrop-blur-sm border-b border-blue-500/20 px-4 py-2 flex-shrink-0">
            <div className="flex items-center gap-2">
              <Plus className="w-4 h-4 text-green-400" />
              <span className="text-sm font-semibold text-green-300">Patched Code</span>
            </div>
          </div>
          <div 
            ref={patchedScrollRef}
            className="font-mono text-sm overflow-y-auto overflow-x-auto flex-1 min-h-0"
            style={{ maxHeight: '100%' }}
          >
            {diff.patched.map((line, idx) => (
              <div
                key={`patch-${idx}`}
                className={`px-4 py-1 flex items-start gap-4 ${
                  line.type === "added"
                    ? "bg-green-500/10 border-l-2 border-green-500"
                    : line.type === "unchanged"
                    ? "bg-slate-900/30"
                    : "bg-slate-900/50"
                }`}
              >
                <span className="text-blue-400/50 text-xs select-none min-w-[3rem] text-right">
                  {line.lineNumber || ""}
                </span>
                <span
                  className={`flex-1 whitespace-pre ${
                    line.type === "added"
                      ? "text-green-300/80"
                      : line.type === "unchanged"
                      ? "text-blue-200/70"
                      : "text-slate-500/50"
                  }`}
                >
                  {line.content || " "}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}

function computeDiff(original: string, patched: string): {
  original: DiffLine[];
  patched: DiffLine[];
} {
  const originalLines = original.split("\n");
  const patchedLines = patched.split("\n");

  // Use a simple longest common subsequence (LCS) approach
  const lcs = computeLCS(originalLines, patchedLines);

  const originalDiff: DiffLine[] = [];
  const patchedDiff: DiffLine[] = [];

  let origIdx = 0;
  let patchIdx = 0;
  let lineNum = 1;

  for (const lcsLine of lcs) {
    // Add lines from original that aren't in LCS (removed)
    while (origIdx < originalLines.length && originalLines[origIdx] !== lcsLine) {
      originalDiff.push({
        type: "removed",
        content: originalLines[origIdx],
        lineNumber: lineNum++,
      });
      patchedDiff.push({
        type: "removed",
        content: "",
      });
      origIdx++;
    }

    // Add lines from patched that aren't in LCS (added)
    while (patchIdx < patchedLines.length && patchedLines[patchIdx] !== lcsLine) {
      originalDiff.push({
        type: "added",
        content: "",
      });
      patchedDiff.push({
        type: "added",
        content: patchedLines[patchIdx],
        lineNumber: lineNum,
      });
      patchIdx++;
      lineNum++;
    }

    // Add the common line (unchanged)
    if (origIdx < originalLines.length && patchIdx < patchedLines.length) {
      originalDiff.push({
        type: "unchanged",
        content: originalLines[origIdx],
        lineNumber: lineNum,
      });
      patchedDiff.push({
        type: "unchanged",
        content: patchedLines[patchIdx],
        lineNumber: lineNum,
      });
      origIdx++;
      patchIdx++;
      lineNum++;
    }
  }

  // Add remaining removed lines
  while (origIdx < originalLines.length) {
    originalDiff.push({
      type: "removed",
      content: originalLines[origIdx],
      lineNumber: lineNum++,
    });
    patchedDiff.push({
      type: "removed",
      content: "",
    });
    origIdx++;
  }

  // Add remaining added lines
  while (patchIdx < patchedLines.length) {
    originalDiff.push({
      type: "added",
      content: "",
    });
    patchedDiff.push({
      type: "added",
      content: patchedLines[patchIdx],
      lineNumber: lineNum++,
    });
    patchIdx++;
  }

  return { original: originalDiff, patched: patchedDiff };
}

function computeLCS(arr1: string[], arr2: string[]): string[] {
  const m = arr1.length;
  const n = arr2.length;
  const dp: number[][] = Array(m + 1)
    .fill(null)
    .map(() => Array(n + 1).fill(0));

  // Build LCS table
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (arr1[i - 1] === arr2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }

  // Reconstruct LCS
  const lcs: string[] = [];
  let i = m;
  let j = n;

  while (i > 0 && j > 0) {
    if (arr1[i - 1] === arr2[j - 1]) {
      lcs.unshift(arr1[i - 1]);
      i--;
      j--;
    } else if (dp[i - 1][j] > dp[i][j - 1]) {
      i--;
    } else {
      j--;
    }
  }

  return lcs;
}


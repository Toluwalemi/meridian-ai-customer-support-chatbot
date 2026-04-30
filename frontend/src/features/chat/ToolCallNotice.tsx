import { ToolCallTrace } from "./types";

type Props = {
  call: ToolCallTrace;
};

export function ToolCallNotice({ call }: Props) {
  return (
    <details className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
      <summary className="cursor-pointer select-none font-medium text-slate-700">
        Called <span className="font-mono text-slate-900">{call.name}</span>
      </summary>
      <div className="mt-2 space-y-1">
        <div>
          <span className="font-medium text-slate-700">Arguments: </span>
          <span className="font-mono">{JSON.stringify(call.arguments)}</span>
        </div>
        <div>
          <span className="font-medium text-slate-700">Result: </span>
          <pre className="mt-1 whitespace-pre-wrap break-words font-mono text-[11px] text-slate-700">
            {call.result_preview}
          </pre>
        </div>
      </div>
    </details>
  );
}

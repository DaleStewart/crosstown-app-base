import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Surface to devtools so we can grep logs after the demo.
    console.error("[ErrorBoundary] render crash", error, info.componentStack);
  }

  handleReset = (): void => {
    this.setState({ error: null });
  };

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div
          role="alert"
          className="m-4 rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-900"
        >
          <p className="font-medium">
            Something went wrong rendering the last response.
          </p>
          <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-[11px] text-red-700">
            {this.state.error.message}
          </pre>
          <button
            type="button"
            onClick={this.handleReset}
            className="mt-3 rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700"
          >
            Dismiss and continue
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

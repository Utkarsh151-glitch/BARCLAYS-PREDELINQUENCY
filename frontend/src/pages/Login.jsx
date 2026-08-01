import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();

  return (
    <div className="h-screen flex items-center justify-center bg-[var(--canvas)]">

      <div className="app-surface p-6 w-[400px]">

        <h2 className="text-2xl font-semibold mb-6">
          Bank Risk Platform Login
        </h2>

        <button
          onClick={() => login("admin")}
          className="w-full mb-3 py-2.5 bg-indigo-600 text-white rounded-xl"
        >
          Login as Bank Admin
        </button>

        <button
          onClick={() => login("officer")}
          className="w-full py-2.5 bg-slate-700 rounded-xl border border-slate-700"
        >
          Login as Risk Officer
        </button>

      </div>
    </div>
  );
}

import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();

  return (
    <div className="h-screen flex items-center justify-center bg-[#0b1220]">

      <div className="bg-slate-900 border border-slate-800 p-10 rounded-2xl w-[400px]">

        <h2 className="text-2xl font-semibold mb-6 text-white">
          Bank Risk Platform Login
        </h2>

        <button
          onClick={() => login("admin")}
          className="w-full mb-4 py-3 bg-indigo-600 rounded-xl"
        >
          Login as Bank Admin
        </button>

        <button
          onClick={() => login("officer")}
          className="w-full py-3 bg-slate-700 rounded-xl"
        >
          Login as Risk Officer
        </button>

      </div>
    </div>
  );
}

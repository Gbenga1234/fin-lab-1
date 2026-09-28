type HealthResponse = {
  status: string;
};

async function getApiHealth(): Promise<HealthResponse | null> {
  try {
    const apiUrl = process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL;
    const res = await fetch(`${apiUrl}/health/`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function Home() {
  const health = await getApiHealth();

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-center gap-6 py-32 px-16 bg-white dark:bg-black">
        <h1 className="text-3xl font-semibold tracking-tight text-black dark:text-zinc-50">
          fin-lab
        </h1>
        <p className="text-lg text-zinc-600 dark:text-zinc-400">
          Next.js frontend + Django/DRF + Celery backend
        </p>
        <div className="flex items-center gap-2 rounded-full border border-black/[.08] px-4 py-2 text-sm dark:border-white/[.145]">
          <span
            className={`h-2 w-2 rounded-full ${
              health?.status === "ok" ? "bg-green-500" : "bg-red-500"
            }`}
          />
          <span>
            API:{" "}
            {health?.status === "ok"
              ? "connected"
              : "unreachable (start the backend)"}
          </span>
        </div>
      </main>
    </div>
  );
}

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-6 py-16">
      <section className="w-full rounded-3xl border border-zinc-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-violet-600">
          CapGen
        </p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-zinc-950">
          AI-powered subtitle generator
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-zinc-600">
          Upload a short-form video, generate synchronized subtitles, customize
          the captions, and export your final video.
        </p>
      </section>
    </main>
  );
}

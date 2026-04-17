import Link from "next/link";

export default function Home() {
  return (
    <section className="flex flex-col items-center justify-center px-6 pt-40 text-center">
      <h1 className="text-7xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
        Every story, every side.
      </h1>
      <p className="mt-4 max-w-xl text-lg text-zinc-600 dark:text-zinc-400">
        Get a fuller picture of the news. We show you how the left, center, and
        right cover the same topics, so you can think for yourself.
      </p>

      <Link
        href="/search"
        className="mt-10 rounded-full bg-zinc-900 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-300"
      >
        Search
      </Link>
    </section>
  );
}

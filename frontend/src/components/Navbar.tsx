import Link from "next/link";

const Navbar = () => {
  return (
    <nav className="relative flex flex-row justify-between items-center p-3 border-b border-neutral-700">
      <Link
        className="text-3xl font-semibold tracking-tight hover:text-neutral-300 transition-colors duration-300"
        href="/"
      >
        News Aggregator
      </Link>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-row gap-4">
        <Link
          className="hover:text-neutral-300 transition-colors duration-300"
          href="/search"
        >
          Search
        </Link>
        <Link
          className="hover:text-neutral-300 transition-colors duration-300"
          href="/about"
        >
          About
        </Link>
      </div>
      <Link
        className="bg-neutral-800 px-4 py-2 rounded-md hover:text-neutral-300 transition-colors duration-300"
        href="/login"
      >
        Login
      </Link>
    </nav>
  );
};

export default Navbar;

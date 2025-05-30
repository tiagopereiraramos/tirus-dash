export default function Header() {
  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
          Sistema RPA BGTELECOM
        </h1>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-500">FastAPI Backend</span>
        </div>
      </div>
    </header>
  );
}
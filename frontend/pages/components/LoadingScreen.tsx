
const LoadingScreen = () => {
    return (
        <div className="min-h-screen bg-white">
            {/* Top Navigation */}
            <nav className="border-b border-gray-300 py-3 px-4 sm:px-6 lg:px-8 bg-black">
                <div className="flex items-center justify-center">
                    <div className="text-3xl font-serif font-bold text-white">The Burda Forward Times</div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {/* Loading Header */}
                <header className="mb-12">
                    {/* Title Skeleton */}
                    <div className="h-12 bg-gray-200 rounded-lg mb-6 animate-pulse" />

                    {/* Summary Skeleton */}
                    <div className="h-20 bg-gray-200 rounded-lg mb-6 animate-pulse" />

                    {/* Author info and controls skeleton */}
                    <div className="flex items-center justify-between border-y border-gray-200 py-4 my-4">
                        <div className="flex items-center space-x-4">
                            <div className="h-4 w-32 bg-gray-200 rounded animate-pulse" />
                            <div className="h-4 w-4 bg-gray-200 rounded animate-pulse" />
                            <div className="h-4 w-24 bg-gray-200 rounded animate-pulse" />
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="h-8 w-24 bg-gray-200 rounded-full animate-pulse" />
                            <div className="h-8 w-24 bg-gray-200 rounded-full animate-pulse" />
                            <div className="h-8 w-20 bg-gray-200 rounded-full animate-pulse" />
                        </div>
                    </div>
                </header>

                {/* Article Content Skeleton */}
                <article className="space-y-6">
                    {/* Paragraphs */}
                    {[...Array(6)].map((_, i) => (
                        <div key={i} className="space-y-3">
                            <div className="h-4 bg-gray-200 rounded animate-pulse w-full" />
                            <div className="h-4 bg-gray-200 rounded animate-pulse w-11/12" />
                            <div className="h-4 bg-gray-200 rounded animate-pulse w-10/12" />
                            <div className="h-4 bg-gray-200 rounded animate-pulse w-9/12" />
                        </div>
                    ))}
                </article>
            </main>

            {/* Footer */}
            <footer className="border-t border-gray-300 py-8 mt-12">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <div className="h-4 w-64 bg-gray-200 rounded animate-pulse mx-auto" />
                </div>
            </footer>
        </div>
    );
};

export default LoadingScreen;
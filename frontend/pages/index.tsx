import { ThumbsDown, ThumbsUp, Video, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import AudioPlayer from './components/AudioPlayer';
import LoadingScreen from './components/LoadingScreen';

const convertMarkdown = (markdown: string): string => {
  return markdown
    .replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" class="w-full h-auto my-2" />')
    .replace(/^# (.*$)/gm, '<h1 class="text-4xl font-serif font-bold my-6 text-black">$1</h1>')
    .replace(/^## (.*$)/gm, '<h2 class="text-2xl font-serif font-bold my-4 text-black">$1</h2>')
    .replace(/^### (.*$)/gm, '<h3 class="text-xl font-serif font-bold my-3 text-black">$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 p-4 rounded-lg my-4 font-mono overflow-x-auto"><code>$1</code></pre>')
    .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded font-mono">$1</code>')
    .replace(/^\- (.*$)/gm, '<li class="ml-6 text-gray-800 my-1">$1</li>')
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-blue-600 hover:underline">$1</a>')
    .replace(/^(?!<[h|l|p|u])(.*$)/gm, '<p class="text-lg leading-relaxed my-4 text-gray-800">$1</p>')
    .replace(/\n\n/g, '<br/>');
};

const sampleArticle = {
  title: "The Rise of Artificial Intelligence in Modern Software Development",
  content: `
# The AI Revolution in Tech

In recent years, **artificial intelligence** has transformed the landscape of software development. From code completion to automated testing, AI tools are becoming increasingly sophisticated and indispensable.

## Key Innovations

The integration of AI in development workflows has led to several breakthrough innovations:

- Intelligent code completion
- Automated bug detection
- Natural language processing for documentation
- Smart code review systems

### Real-World Applications

Here's a simple example of AI-assisted code:

\`\`\`python
def analyze_sentiment(text):
    # AI-powered sentiment analysis
    sentiment_score = ai_model.predict(text)
    return sentiment_score
\`\`\`

The future of coding might look very different. As noted in [this research paper](https://example.com), AI could automate up to 70% of routine coding tasks.

![AI Coding Assistant](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ1hEuGfRL7DJLZYWDSbgmubhGSbpvDQzIdsA&s)

*The above image shows an AI coding assistant in action.*

## The Human Element

Despite these advances, human developers remain crucial. Their role is evolving from writing every line of code to:

- Architectural decision-making
- Problem-solving
- Code review and validation
- Strategic planning

The synergy between human creativity and AI capabilities will define the next era of software development.
`,
  author: "Sarah Johnson",
  date: "2024-02-15",
  summary: "How artificial intelligence is revolutionizing the software development industry, transforming traditional coding practices, and creating new opportunities for developers."
};

export default function Home() {
  //const [article, setArticle] = useState(sampleArticle);
  interface Article {
    title: string;
    content: string;
    author: string;
    date: string;
    summary: string;
  }

  const [article, setArticle] = useState<Article | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [rating, setRating] = useState<'up' | 'down' | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentArticleIndex, setCurrentArticleIndex] = useState(0);
  const [showReel, setShowReel] = useState(false);


  const audioRef = useRef<HTMLAudioElement | null>(null);

  const articles = [
    { file: 'article.txt', audio: 'northvolt_podcast.wav', reel: 'https://cdn.creatomate.com/renders/d6a339c9-b84d-4168-9627-b494915d759f.mp4' },
    { file: 'zio.txt', audio: 'test_audio.wav', reel: 'https://cdn.creatomate.com/renders/5fe45a4e-651a-4999-bfec-df6991461051.mp4' },
    // Add more articles as needed
  ];
  const generateArticle = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/next-article/');
      if (!response.ok) throw new Error('Failed to fetch article');
      const data = await response.json();

      /* const response = await fetch(`/${articleFile}`);
      if (!response.ok) throw new Error('Failed to fetch article');
      const text = await response.text(); */
      setArticle({
        title: "Article from Text File",
        content: data.article,
        author: "Unknown",
        date: new Date().toISOString().split('T')[0],
        summary: "This is an article fetched from a text file in the public folder."
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };
  const handleNextArticle = async () => {
    // Stop audio if playing
    if (audioRef.current && isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    }

    // Reset rating
    setRating(null);

    // Update index and load next article
    const nextIndex = (currentArticleIndex + 1) % articles.length;
    setCurrentArticleIndex(nextIndex);
    await generateArticle();

    // Update audio source
    if (audioRef.current) {
      audioRef.current.src = articles[nextIndex].audio;
      setCurrentTime(0);
    }
  };


  // Commented out fetch request for now

  useEffect(() => {
    /*const fetchArticle = async () => {
      try {
        const response = await fetch('http://localhost:8000/get_article');
        if (!response.ok) throw new Error('Failed to fetch article');
        const data = await response.json();
        setArticle(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchArticle();*/

    audioRef.current = new Audio(articles[currentArticleIndex].audio);

    audioRef.current.addEventListener('timeupdate', handleTimeUpdate);
    audioRef.current.addEventListener('loadedmetadata', handleLoadMetadata);
    audioRef.current.addEventListener('ended', () => setIsPlaying(false));

    return () => {
      if (audioRef.current) {
        audioRef.current.removeEventListener('timeupdate', handleTimeUpdate);
        audioRef.current.removeEventListener('loadedmetadata', handleLoadMetadata);
        audioRef.current.removeEventListener('ended', () => setIsPlaying(false));
        audioRef.current.pause();
      }
    };
  }, [currentArticleIndex]);
  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = Number(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleRating = (type: 'up' | 'down') => {
    setRating(rating === type ? null : type);
  };


  if (isLoading) {
    return <LoadingScreen />;
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-600 text-xl">{error}</div>
      </div>
    );
  }
  if (!article) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-white gap-8">
        {/* Logo Image */}
        <img
          src="/images.jpeg"
          alt="Logo"
          className="w-64 h-auto" // Adjust width as needed
        />

        {/* Button */}
        <button
          onClick={() => generateArticle()}
          className="bg-black text-white px-6 py-3 rounded-lg text-lg font-semibold hover:bg-gray-800 transition-colors duration-200"
        >
          Generate Article
        </button>
      </div>
    );
  };





  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <nav className="border-b border-gray-300 py-3 px-4 sm:px-6 lg:px-8 bg-black">
        <div className="flex items-center justify-center">
          <div className="text-sm text-gray-500"></div>
          <div className="text-3xl font-serif font-bold">The Burda Forward Times</div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Article Header */}
        <header className="mb-12">
          {/* <h1 className="text-5xl font-serif font-bold mb-4">{article.title}</h1>
          <p className="text-xl text-gray-700 mb-6 font-serif leading-relaxed">
            {article.summary}
          </p> */}

          {/* Author info and controls row */}
          <div className="flex items-center justify-between border-y border-gray-700 py-4 my-4">
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <div className="font-medium">By Burda Forward</div>
              <div>|</div>
              <div>{new Date(article.date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}</div>
            </div>
            {/* Podcast and rating controls */}
            <div className="flex items-center space-x-4">
              {/* Next Article Button */}
              <button
                onClick={handleNextArticle}
                className="bg-black text-white px-4 py-1 rounded-full hover:bg-gray-800 transition-colors duration-200 text-sm"
              >
                Next Article
              </button>
              {/* Reel button */}
              <button
                onClick={() => setShowReel(true)}
                className="flex items-center space-x-2 px-3 py-1 rounded-full bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors duration-200"
              >
                <Video size={16} />
                <span className="text-sm">Watch Reel</span>
              </button>
              {/* Podcast button */}
              <AudioPlayer
                isPlaying={isPlaying}
                onPlayPause={handlePlayPause}
                currentTime={currentTime}
                duration={duration}
              />

              {/* Rating buttons */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleRating('up')}
                  className={`p-1 rounded-full hover:bg-gray-700 transition-colors duration-200
                    ${rating === 'up' ? 'text-green-400' : 'text-gray-400'}`}
                >
                  <ThumbsUp size={20} />
                </button>
                <button
                  onClick={() => handleRating('down')}
                  className={`p-1 rounded-full hover:bg-gray-700 transition-colors duration-200
                    ${rating === 'down' ? 'text-red-400' : 'text-gray-400'}`}
                >
                  <ThumbsDown size={20} />
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Article Content */}
        <article
          className="prose prose-lg max-w-none"
          dangerouslySetInnerHTML={{ __html: convertMarkdown(article.content) }}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-300 py-8 mt-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} The Burda Forward Times. All rights reserved.
        </div>
      </footer>
      {showReel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-black rounded-lg w-full max-w-[320px] relative"> {/* Reduced from 400px to 320px */}
            <button
              onClick={() => setShowReel(false)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 transition-colors duration-200"
            >
              <X size={24} />
            </button>
            <div className="aspect-[9/16] w-full">
              <iframe
                src={articles[currentArticleIndex].reel}
                className="w-full h-full rounded-lg"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      )}
    </div >
  );
}
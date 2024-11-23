import { Pause, Play } from 'lucide-react';

const AudioPlayer = ({ isPlaying, onPlayPause, currentTime, duration }) => {
    // Generate bars for visualization
    const bars = Array.from({ length: 20 }, (_, i) => {
        // Create varying heights for bars to simulate waveform
        const height = Math.random() * 16 + 8; // Random height between 8-24px
        return (
            <div
                key={i}
                className={`w-1 rounded-full transition-all duration-700 mx-px ${(i * duration) / 20 <= currentTime
                    ? 'bg-black'
                    : 'bg-gray-200'
                    }`}
                style={{ height: `${height}px` }}
            />
        );
    });

    return (
        <button
            onClick={onPlayPause}
            className="flex items-center space-x-3 px-4 py-2"
        >
            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-black">
                {isPlaying ? (
                    <Pause size={20} className="text-white" />
                ) : (
                    <Play size={20} className="text-white ml-1" />
                )}
            </div>
            <div className="flex items-center h-6">
                {bars}
            </div>
        </button>
    );
};

export default AudioPlayer;
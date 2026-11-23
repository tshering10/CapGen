# AI-Powered Subtitle Generator

An AI-powered subtitle generator and lightweight editor for short-form videos such as Instagram Reels, YouTube Shorts, and TikTok videos.

Upload an already-edited video, automatically generate synchronized subtitles, customize their appearance and positioning, and download the final video with embedded captions or export subtitles as an SRT file.

## Features

### Core Features (V1)

- **Video Upload:** Upload already-edited short-form videos.
- **Automatic Transcription:** Generate subtitles using AI-powered speech recognition.
- **Language Selection:** Select the spoken language manually or use automatic language detection.
- **Subtitle Editing:** Edit, add, delete, split, and merge subtitle segments.
- **Timestamp Editing:** Adjust subtitle start and end times.
- **Caption Presets:** Choose from predefined subtitle styles.
- **Subtitle Customization:** Customize font size, colors, alignment, and other basic styling options.
- **Subtitle Positioning:** Drag and reposition captions within the video preview.
- **Video Preview:** Preview subtitles and their styling before exporting.
- **Video Export:** Download the video with permanently embedded subtitles.
- **SRT Export:** Download subtitles separately in SRT format.
- **No Registration Required:** Use the application without creating an account.

## Tech Stack

### Backend
- Python
- FastAPI
- faster-whisper
- FFmpeg
- Celery
- Redis

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS

### Subtitle Processing
- SRT (SubRip Subtitle)
- ASS (Advanced SubStation Alpha)

### Infrastructure
- Docker
- Temporary local file storage

## Application Workflow

1. User uploads an already-edited short-form video.
2. User selects a spoken language or enables automatic language detection.
3. The backend extracts the audio using FFmpeg.
4. faster-whisper processes the audio and generates text with timestamps.
5. The application generates structured subtitle data.
6. User previews and edits the generated subtitles.
7. User selects a caption preset and customizes subtitle appearance and positioning.
8. User exports the final video with embedded subtitles or downloads the SRT file.
9. Temporary files are automatically cleaned up after processing.

## Project Architecture

The application consists of three main components:

- **Frontend:** Handles video uploads, subtitle editing, visual customization, and previews.
- **Backend:** Manages uploads, transcription requests, job processing, and subtitle data.
- **Processing Engine:** Handles audio extraction, AI transcription, subtitle generation, and final video rendering.

## Development Roadmap

- [ ] Phase 1: Build the AI transcription engine.
- [ ] Phase 2: Develop the FastAPI backend and background processing.
- [ ] Phase 3: Build the Next.js frontend.
- [ ] Phase 4: Implement the subtitle editor.
- [ ] Phase 5: Implement caption presets and positioning.
- [ ] Phase 6: Implement MP4 and SRT exports.
- [ ] Phase 7: Testing, optimization, and deployment.

## Project Scope

The initial release focuses exclusively on short-form videos.

The application is designed as a lightweight subtitle generation and editing tool, not a full video editing platform.

User authentication, long-video processing, subtitle translation, advanced animations, and extensive video editing capabilities are outside the initial V1 scope.

## Future Improvements

- Multilingual subtitle translation.
- Additional caption templates and animations.
- Word-by-word highlighting.
- Custom font support.
- Improved subtitle synchronization.
- Additional language support.

## License

To be decided.
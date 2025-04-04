# Interactive CPR Training Module

An AI-powered CPR training application that provides real-time feedback on CPR technique using computer vision and voice interaction.

## Features

- Real-time motion analysis using computer vision
- Immediate audio-visual feedback on CPR technique
- Voice command interface for asking questions
- Interactive Q&A system with AI-powered responses
- Real-time metrics display (compression rate, depth, etc.)

## Prerequisites

- Python 3.8 or higher
- Webcam
- Microphone
- Display monitor

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd cpr-training-module
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key
```

## Usage

Run the main application:
```bash
python main.py
```

## Project Structure

- `main.py`: Main application entry point
- `modules/`
  - `vision.py`: Computer vision and pose estimation
  - `feedback.py`: Audio-visual feedback system
  - `voice.py`: Speech recognition and text-to-speech
  - `qa.py`: Question-answering system
  - `ui.py`: User interface components

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. #   c p r - t r a i n i n g  
 
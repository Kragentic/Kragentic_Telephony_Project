# Modular AI Communication Platform (MCP)

## Overview

The Modular AI Communication Platform (MCP) is designed to manage inbound and outbound calls using AI-powered voice agents. It integrates with Twilio for telephony, LiveKit for real-time voice streaming, STT (Speech-to-Text), TTS (Text-to-Speech), and LLM-based conversational AI (OpenAI/Claude). The platform supports RAG (Retrieval-Augmented Generation), CAG (Conversational Augmentation), campaign logic, list management, compliance features (e.g., consent before recording), and deployment on Fly.io for scalability and resilience.

## Features

- Inbound and outbound calls via Telnyx integration
- Call dispatch rules with consent handling
- Modular AI agents built with LangChain and OpenAI/Claude APIs
- STT (Google Speech API, SpeechRecognition, or Whisper)
- TTS (gTTS, pyttsx3, or ElevenLabs API optional)
- Voice streaming through LiveKit
- Compliance and consent management
- Campaign and dispatch rules engine
- RAG/CAG augmentation with LangChain
- Analytics and logging
- Deployment on Fly.io with Cloudflare for CDN, DNS, and security

## Getting Started

### Prerequisites

- Elixir
- Python
- Docker
- Fly.io account

### Installation

1. Clone the repository
2. Install dependencies
3. Build and run the application

### Deployment

1. Set up Fly.io
2. Deploy the application using the provided Dockerfile and fly.toml configuration

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

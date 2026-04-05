# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- CI pipeline with GitHub Actions (lint, type check, tests on Python 3.12 & 3.13)
- Model selection in the frontend: dropdown in the header to switch between Ollama models (e.g. qwen2.5, gemma3)
- API endpoint `GET /api/models` to list all available Ollama models
- Initial project structure with FastAPI backend and vanilla JS frontend
- AI image analysis with Ollama vision model (LLaVA)
- Automatic price estimation by scraping Kleinanzeigen.de and eBay
- Category mapping with AI-powered fuzzy matching
- Browser automation with Playwright for Kleinanzeigen.de
- Web UI with drag & drop image upload
- Batch processing for multiple items
- Article editor for reviewing before publishing
- Configuration via .env file (pydantic-settings)
- Unit tests for models, config, parser, and estimator

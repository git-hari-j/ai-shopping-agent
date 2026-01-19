# Setup Guide

## Prerequisites
- Python 3.12+
- `uv` (recommended) or `pip`
- Adobe Commerce / Magento 2 instance

## Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd <repo-dir>
   ```

2. **Backend Setup**
   ```bash
   cd adobe-commerce-agents
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Copy `.env.example` to `.env`.
   - Set `MAGENTO_URL` to your Magento instance.
   - Set `OPENAI_API_KEY` (or other LLM provider keys).

4. **Run the Application**
   ```bash
   uvicorn app:app --reload
   ```

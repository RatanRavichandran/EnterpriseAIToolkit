Built as part of Tata Technologies Innovent 2024 Hackathon, this project showcases a multi-domain Generative & Agentic AI platform designed to solve real business challenges across e-commerce, food & beverage, automotive, and customer support through modular workflows, data pipelines, and interactive dashboard

## Solution Pillars

Our platform addresses four critical business domains with integrated AI-powered solutions:

### 🍽️ **Food & Beverage Operations**
- **Food Waste Reduction:** AI-powered analytics dashboard for tracking waste patterns, optimizing inventory, and reducing food spoilage
- **Inventory Intelligence:** Smart inventory management with predictive analytics, automated reordering, and supplier performance tracking
- **Recipe Development:** AI-assisted recipe creation and optimization using customer preferences and ingredient availability

### 🛒 **E-commerce Personalization**
- **Product Analysis:** Automated product scraping, sentiment analysis, and competitive intelligence
- **User Profiling:** Advanced customer segmentation and behavior analysis with personalized recommendations
- **Recommendation Engines:** Hybrid collaborative filtering and content-based systems with vector similarity search
- **Product Summarization:** AI-generated product summaries and insights for better customer experience

### 🚗 **Automotive Experience**
- **Car Recommendation Bot:** Intelligent vehicle matching based on customer preferences, budget, and requirements
- **Warning Light Assistant:** AI-powered diagnostic support for dashboard warning lights and maintenance issues
- **Warranty Quote System:** Automated warranty cost estimation and service scheduling
- **Chatbot Support:** Conversational AI for customer inquiries and technical support

### 🎫 **Customer Support Intelligence**
- **Ticket Analysis Dashboard:** Comprehensive sentiment analysis, topic classification, and automated routing
- **User Profile Generator:** Automated PDF generation of customer profiles and analytics reports
- **Real-time Monitoring:** Daily and monthly reporting with trend analysis and performance metrics

### 🔍 **Review Intelligence**
- **Natural Language Query Processing:** Convert user questions into SQL queries for review analysis
- **Sentiment Analysis:** Advanced review sentiment classification and aspect-based analysis
- **Review Authenticity:** Detection of fake reviews and quality assessment

## Repository Layout

```
TATA/
+-- README.md
+-- requirements.txt
+-- .gitignore
+-- docs/
|   +-- init_to_winit_tata.pdf
|   +-- demos/             # Demo videos & audio narrations
+-- data/
|   +-- raw/               # Source CSV/PKL assets used by notebooks and apps
|   |   +-- bigbasket_products_*.csv
|   |   +-- food_ingredients_with_images.csv
|   |   +-- train_essays.csv, test_essays.csv
|   |   +-- cluster_centers.pkl, tfidf_vectorizer.pkl
|   +-- reference/         # Small lookup tables & sample profiles
|   |   +-- amazon_products_list.csv
|   |   +-- automotive/    # Warranty PDFs and automotive data
|   |   +-- inventory/     # Inventory metrics and supplier data
|   |   +-- recipe/       # Recipe and sales datasets
|   |   +-- sample_user_profile.txt
|   |   +-- ecommerce.db  # SQLite database
|   +-- processed/         # Generated artefacts (ignored by git)
|   +-- external/          # Large third-party downloads (ignored by git)
|       +-- glove.6B.50d.txt
+-- notebooks/
|   +-- ecommerce/
|       +-- product_recommendations.ipynb
|       +-- updated_test.ipynb
+-- src/
|   +-- ecommerce/
|   |   +-- apps/          # Streamlit apps for product analysis & profiling
|   |   |   +-- product_analyzer/streamlit_app.py
|   |   |   +-- product_summary/streamlit_app.py
|   |   |   +-- user_profile_manager/streamlit_app.py
|   |   +-- pipelines/     # Offline recommendation workflows & demos
|   |       +-- amazon_product_cli.py
|   |       +-- collaborative_filtering_demo.py
|   |       +-- product_recommendations/
|   |           +-- product_recommendation_service.py
|   |           +-- vector_search_demo.py
|   +-- operations/        # Food & beverage dashboards
|   |   +-- food_waste/streamlit_app.py
|   |   +-- inventory/streamlit_app.py
|   |   +-- recipe_development/streamlit_app.py
|   +-- customer_support/  # Ticket analytics utilities
|   |   +-- ticket_analysis_dashboard.py
|   |   +-- user_profile_pdf_generator.py
|   +-- automotive/        # Warranty, chatbot & advisor prototypes
|   |   +-- car_recommendation_bot.py
|   |   +-- chatbot_app.py
|   |   +-- warning_light_assistant.py
|   |   +-- warranty_quote_app.py
|   +-- review_intelligence/ # Review authenticity exploration
|       +-- app/main.py
|       +-- scripts/       # Analysis and query generation scripts
|       +-- db/           # Database configuration and migrations
|       +-- data/         # Review datasets and processed vectors
+-- archive/               # Legacy dumps kept out of version control
    +-- legacy_assets/
        +-- tata_codes_backup.zip
```

## Getting Started

1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Environment variables**
   - Copy any `*.env.example` files beside the Streamlit apps into `.env` and add your keys.
   - At minimum set `OPENAI_API_KEY`. Optional: `CHROMEDRIVER_PATH` for Selenium, database DSNs, etc.
3. **Optional data downloads**
   - Place the 50d GloVe embeddings in `data/external/glove.6B.50d.txt` (see README inside the folder).
   - Automotive warranty PDFs belong in `data/reference/automotive/` (see folder README for schema expectations).

## Running the Applications

### 🛒 **E-commerce Applications**
```bash
# Product Analysis & Scraping
streamlit run src/ecommerce/apps/product_analyzer/streamlit_app.py

# Product Summarization
streamlit run src/ecommerce/apps/product_summary/streamlit_app.py

# User Profile Management
streamlit run src/ecommerce/apps/user_profile_manager/streamlit_app.py
```

### 🍽️ **Operations & Food Services**
```bash
# Food Waste Reduction Dashboard
streamlit run src/operations/food_waste/streamlit_app.py

# Inventory Intelligence
streamlit run src/operations/inventory/streamlit_app.py

# Recipe Development
streamlit run src/operations/recipe_development/streamlit_app.py
```

### 🚗 **Automotive Applications**
```bash
# Car Recommendation Bot
streamlit run src/automotive/car_recommendation_bot.py

# Warning Light Assistant
streamlit run src/automotive/warning_light_assistant.py

# Warranty Quote System
streamlit run src/automotive/warranty_quote_app.py

# General Chatbot Support
streamlit run src/automotive/chatbot_app.py
```

### 🎫 **Customer Support**
```bash
# Ticket Analysis Dashboard
streamlit run src/customer_support/ticket_analysis_dashboard.py

# User Profile PDF Generator
streamlit run src/customer_support/user_profile_pdf_generator.py
```

### 🔍 **Review Intelligence**
```bash
# Review Analysis App
streamlit run src/review_intelligence/app/main.py
```

Each application includes built-in configuration guidance and will highlight any missing API keys or dependencies before execution.

## Technical Features & AI Capabilities

### 🤖 **AI/ML Technologies**
- **OpenAI GPT Integration:** Conversational AI, text analysis, and content generation
- **Vector Embeddings:** GloVe embeddings for semantic similarity and recommendation systems
- **TF-IDF Vectorization:** Content-based filtering and text analysis
- **Collaborative Filtering:** SVD-based recommendation algorithms
- **Sentiment Analysis:** TextBlob and OpenAI-powered sentiment classification
- **Web Scraping:** Selenium and BeautifulSoup for automated data collection

### 🔧 **Data Processing**
- **SQLite Database:** Structured data storage for user profiles and reviews
- **CSV Processing:** Pandas-based data manipulation and analysis
- **PDF Generation:** Automated report and profile generation
- **Vector Storage:** Efficient similarity search and recommendation systems
- **Real-time Analytics:** Live dashboard updates and monitoring

### 🌐 **Web Technologies**
- **Streamlit:** Interactive web applications and dashboards
- **Selenium WebDriver:** Automated browser interactions and scraping
- **BeautifulSoup:** HTML parsing and content extraction
- **Requests:** HTTP client for API interactions and web scraping

### 📊 **Analytics & Visualization**
- **Interactive Dashboards:** Real-time data visualization and monitoring
- **Automated Reporting:** PDF generation with charts and analytics
- **Trend Analysis:** Historical data analysis and pattern recognition
- **Performance Metrics:** KPI tracking and business intelligence

## Offline Workflows & Notebooks

- `src/ecommerce/pipelines/collaborative_filtering_demo.py` expects personalised CSVs in `data/reference/personalized_ecommerce/` and demonstrates feedback-aware SVD recommendations.
- `src/ecommerce/pipelines/product_recommendations/` hosts vector-similarity demos and a TF�IDF recommendation service that persists models under `data/processed/recommendations/`.
- Jupyter notebooks under `notebooks/ecommerce/` explore clustering and recommendation experiments used during the hackathon pitch.

## Application Details

### 🛒 **E-commerce Suite**
- **Product Analyzer:** Automated web scraping of e-commerce sites with sentiment analysis and competitive intelligence
- **Product Summary:** AI-generated product summaries and insights for better customer experience
- **User Profile Manager:** Advanced customer segmentation with SQLite database integration and personalized recommendations

### 🍽️ **Operations Management**
- **Food Waste Dashboard:** Real-time waste tracking with predictive analytics and optimization recommendations
- **Inventory Intelligence:** Smart inventory management with automated reordering and supplier performance tracking
- **Recipe Development:** AI-assisted recipe creation using customer preferences and ingredient availability

### 🚗 **Automotive Solutions**
- **Car Recommendation Bot:** Intelligent questionnaire-based vehicle matching for Indian market
- **Warning Light Assistant:** AI-powered diagnostic support for dashboard warning lights and maintenance issues
- **Warranty Quote System:** Automated cost estimation with component pricing and labor calculations
- **Chatbot Support:** Conversational AI for general automotive inquiries and technical support

### 🎫 **Customer Support Intelligence**
- **Ticket Analysis Dashboard:** Multi-tab interface with sentiment analysis, topic classification, urgency detection, and automated routing
- **User Profile PDF Generator:** Automated PDF generation of comprehensive customer profiles and analytics reports

### 🔍 **Review Intelligence Platform**
- **Natural Language Query Interface:** Convert user questions into SQL queries for review analysis
- **Advanced Analytics:** Sentiment classification, aspect-based analysis, and review authenticity detection
- **Database Integration:** SQLite-based review storage with vectorized embeddings for similarity search

## Datasets & Artefacts

| Location | Description |
|----------|-------------|
| `data/raw/` | Core datasets including BigBasket product catalog, Amazon reference data, essay sentiment samples, TF-IDF models, and clustering artifacts |
| `data/reference/` | Supporting data including automotive warranty information, inventory metrics, recipe datasets, sample customer profiles, and SQLite databases |
| `data/external/` | Third-party resources like GloVe embeddings (50d vectors) for semantic similarity |
| `data/processed/` | Generated artifacts including trained models, vectorized data, and recommendation outputs |
| `docs/demos/` | Demo videos and audio narrations for pitch presentations |
| `archive/legacy_assets/` | Original ZIP bundle retained for provenance but ignored by git |

Large or proprietary files are either ignored or documented so they can be restored without bloating the repository.

## Extending the Project

### 🚀 **Future Enhancements**
- **Integrated Dashboard:** Build orchestration around the modular Streamlit apps to produce a unified business intelligence cockpit
- **Local AI Models:** Swap OpenAI APIs for local models (Llama, Mistral) by adapting the helper wrappers in each module
- **Vector Databases:** Integrate FAISS/Chroma for faster contextual lookups across product descriptions and knowledge bases
- **Production Pipelines:** Harden data ingestion with scheduled pipelines, API integrations, and real-time data streaming
- **Microservices Architecture:** Containerize applications with Docker and implement Kubernetes orchestration
- **Advanced Analytics:** Implement real-time ML model training and A/B testing frameworks

### 🔧 **Technical Improvements**
- **Database Scaling:** Migrate from SQLite to PostgreSQL/MongoDB for production workloads
- **Caching Layer:** Implement Redis for improved performance and reduced API costs
- **Monitoring:** Add comprehensive logging, metrics collection, and alerting systems
- **Security:** Implement authentication, authorization, and data encryption
- **Testing:** Add comprehensive unit tests, integration tests, and end-to-end testing frameworks

### 📈 **Business Value Additions**
- **Multi-language Support:** Extend applications to support regional languages for Indian market
- **Mobile Applications:** Develop React Native or Flutter apps for mobile access
- **API Gateway:** Create RESTful APIs for third-party integrations and mobile apps
- **Advanced Reporting:** Implement automated business intelligence and executive dashboards

## Quick Start Guide

### 🎯 **For Business Users**
1. **Food & Beverage Operations:** Start with `src/operations/food_waste/streamlit_app.py` for waste reduction insights
2. **E-commerce Teams:** Use `src/ecommerce/apps/product_analyzer/streamlit_app.py` for competitive analysis
3. **Automotive Dealers:** Launch `src/automotive/car_recommendation_bot.py` for customer vehicle matching
4. **Customer Support:** Access `src/customer_support/ticket_analysis_dashboard.py` for ticket analytics

### 🔧 **For Developers**
1. **Clone and Setup:** Follow the Getting Started section above
2. **API Configuration:** Set `OPENAI_API_KEY` environment variable
3. **Data Preparation:** Place required datasets in `data/raw/` and `data/reference/`
4. **Run Applications:** Use the provided streamlit commands for each module

### 📊 **Key Metrics to Track**
- **E-commerce:** Product recommendation accuracy, user engagement rates
- **Operations:** Waste reduction percentage, inventory turnover improvements
- **Automotive:** Customer satisfaction scores, warranty claim processing time
- **Support:** Ticket resolution time, sentiment trend analysis

## Credits & References

- **Original Concept Deck:** [`docs/init_to_winit_tata.pdf`](docs/init_to_winit_tata.pdf)
- **Demo Recordings:** `docs/demos/`
- **Team:** Init_to_Winit (Sayli, Ratan, Sri Bharath, Shriyans)
- **Hackathon:** Tata Technologies Init_to_Winit 2024

### 📚 **Technical References**
- OpenAI GPT API Documentation
- Streamlit Framework Documentation
- GloVe Embeddings Research Paper
- Collaborative Filtering Algorithms (SVD)
- Web Scraping Best Practices (Selenium, BeautifulSoup)

Feel free to open issues or suggestions as you adapt the prototypes for your specific use cases.

# 🔍 NuNER

NuNER is one of the main data-mining components of the Panopticon platform. It contributes to finding a resolution to the 
problem of having to parse very large volumes of unstructured data as a continuous streaming requirement.

> PLEASE NOTE: While this platform will at times heavily rely on A.I. the concept behind the implementation of tools 
> is always the human factor, and not "A.I. for A.I.'s sake."
> The aim is to enhance human-driven research and investigation. At no point should anything within these repositories suggest "automation" 
> even when wording like that may be used to accurately describe the workings of the technology.
> In the very best-case scenarios, we hope these tools to help prioritise and focus your work when dealing with non-human level amounts of
> data that have become a common aspect of the job these days, and potentially reduce the onboarding barrier of domains of interest, for which
> a lack of domain-knowledge may exist.

---

## Overview

NuNER is a critical component of the Panopticon platform, designed to extract, analyze, and enrich information from unstructured text data. 
It's an integral part of one of the most advanced free and unrestricted investigation toolkits available today.

![neo4j1.png]()

### The Panopticon Platform

Panopticon is one of the most advanced investigation toolkits available to anyone who has a need for it. 
It is designed by drawing on the expertise of real-world practitioners, modeling their methods and approach, while identifying areas 
that could be optimized or otherwise enhanced by current technological advancements. 

This platform empowers investigators with cutting-edge tools and techniques, streamlining complex research processes and uncovering 
insights that might otherwise remain hidden.

### Evolution of NuNER

1. **Original Concept**: Initially conceived to use the NuNER model from the GLiNER family for high-performance, cost-effective 
   named entity recognition and relationship extraction.

2. **Current Implementation**: Utilizes OpenAI's GPT models as an interim solution, ensuring continued functionality 
   and integration within the Panopticon platform, keeping development across the board unblocked.

3. **Future Direction**: Aims to transition back to the NuNER model, combining the accuracy of large language models with the 
   efficiency of specialized NER systems, while incorporating advanced AI-driven research and enrichment capabilities.

---

## 🚀 Features & Roadmap

- [x] Integration with OpenAI GPT models for text analysis
- [x] Support for multiple graph databases (Neo4j, JanusGraph, ArangoDB, TigerGraph)
- [x] FastAPI-based API for receiving data from Foucault
- [x] Redis Queue for task management and processing
- [x] Basic entity and relationship extraction
- [x] Timeline extraction for entities
- [ ] Implementation of NuNER model from GLiNER family
- [ ] Enhanced entity disambiguation
- [ ] Improved relationship extraction with confidence scoring
- [ ] First-class integration with Yet-to-be designed "Case File" data model
- [ ] Real-time processing and graph updates
- [ ] Advanced query interface for researchers
- [ ] Integration with external knowledge bases for entity enrichment
- [ ] Customizable extraction rules for domain-specific intelligence
- [ ] Automated report generation based on extracted intelligence
- [ ] Multi-language support for global intelligence gathering
- [ ] Sentiment analysis for extracted entities and relationships
- [ ] Automatic periodic data consolidation
  - [ ] Merging entities incorrectly recognized as distinct
  - [ ] Resolving conflicting information
  - [ ] Identifying and removing duplicate data
- [ ] AI-driven auto-enrichment
  - [ ] Autonomous identification of knowledge gaps
  - [ ] Web scraping and analysis for filling information gaps
  - [ ] Integration of newly discovered information into the knowledge graph
- [ ] Anomaly detection in data patterns
- [ ] Predictive analytics based on historical data and trends
- [ ] Interactive visualization tools for complex relationship networks
- [ ] API for third-party integrations and custom applications
- [ ] Secure, role-based access control for sensitive information
- [ ] Automated backup and version control of the knowledge graph
- [ ] Integration with training pipeline to automatically enhance the machine learning models

## 🔗 Integration with Panopticon Platform

NuNER is tightly integrated with other components of the Panopticon platform:

- **Foucault Browser Extension**: Primary source of input for NuNER, capturing web content during research.
- **Automated Background Processing**: Allows researchers to focus on following leads while NuNER extracts valuable intelligence.

## 🤖 AI-Driven Research and Enrichment

NuNER is evolving to include sophisticated AI agents capable of autonomous research and data enrichment:

1. **Gap Analysis**: AI agents continuously analyze the knowledge graph to identify information gaps or inconsistencies.

2. **Autonomous Web Research**: Based on identified gaps, agents formulate queries and conduct web searches to find relevant information.

3. **Data Extraction and Verification**: New information is extracted from found sources, cross-referenced with existing data, and verified for accuracy.

4. **Graph Integration**: Verified data is seamlessly integrated into the knowledge graph, enriching existing entities and relationships.

5. **Feedback Loop**: The system learns from successful enrichments to improve future research efficiency and accuracy.

This autonomous enrichment process ensures that the knowledge graph remains up-to-date and comprehensive, providing researchers 
with the most current and relevant information possible.

---

## 🛠️ Setup & Installation

The entire platform has an infrastructure designed to be mostly hands-off to leave more time to focus on development, or usage.

The only thing you have to configure are any API tokens of external services, and optionally you can switch to one or more
alternative graph database backends.

- Neo4J (default)
- ArangoDB
- TigerGraph
- JanusGraph

## 🏃 Running the Project

Place the `docker-compose.yml` at the top-level directory that also houses the other services of the platform.

```
docker compose up
```

## 📊 Usage

[Usage instructions]

## 🔧 Configuration

[Configuration instructions]

## 📈 Visualization

[Visualization instructions]

## 🤝 Contributing

Contributions to NuNER are welcome! Please refer to the main Panopticon repository for contribution guidelines.

## 📄 License

This project is licensed under the [Unlicense](https://unlicense.org/). This is free and unencumbered software released into the public domain. For more information, please refer to the [LICENSE](./LICENSE) file in the repository or visit the Unlicense website.

---

For more information on the Panopticon platform and its components, including the Foucault browser extension, please visit the main [Panopticon Repository](https://github.com/your-repo/panopticon).


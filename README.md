# দেশমৃত্তিকা | DeshMrittika
## BHUMI-SYNC — Smart Land Record Verification & Intelligence Platform

**Tagline:** *Your Land, Our Responsibility — আপনার জমি, আমাদের দায়িত্ব*

**Project Track:** LandTech Software  
**Event:** LandTech 2026 Innovation Hackathon  
**Institution:** Daffodil International University (DIU)

---

## 1. Executive Summary

**DeshMrittika (দেশমৃত্তিকা), powered by BHUMI-SYNC**, is a proposed digital land-management and verification platform designed to support greater transparency, traceability, and informed decision-making in Bangladesh's land administration ecosystem.

Land-related transactions frequently require citizens to examine multiple documents, ownership records, mutation status, tax information, and other relevant records. Fragmented information and delays in verification can make it difficult to identify inconsistencies before a transaction takes place.

DeshMrittika addresses these challenges through a unified software prototype that brings together digital record exploration, document-integrity checks, ownership-history analysis, transaction-risk screening, mutation workflow tracking, and cadastral mapping.

The platform is designed to assist citizens, prospective land buyers, and authorized officials by presenting relevant information and potential risk indicators in a structured and explainable format.

**DeshMrittika is a technology prototype, not an official government service.** Its intended role is to support verification and administrative review; it does not independently establish legal ownership or replace statutory procedures and decisions by competent authorities.

## 2. Vision and Objectives

Our vision is to contribute to a more transparent, accessible, and accountable land-information ecosystem in Bangladesh.

The project aims to:

- Improve the accessibility and organization of land-related information.
- Support the identification of potentially inconsistent ownership and transaction records.
- Facilitate document-integrity verification and traceable review workflows.
- Help prospective buyers conduct preliminary due diligence before purchasing land.
- Support the visualization of cadastral parcels and relevant public-land risk indicators.
- Provide a foundation for future integration with authorized government systems, subject to institutional approval, data governance, and applicable law.

## 3. Key Capabilities

### Digital Land Record Exploration
Organizes land-record information into a structured format to support easier search, review, and retrieval.

### Document Integrity Verification
Uses document hashing and verification mechanisms to help identify whether a digital document has changed since its reference hash was generated.

### Ownership and Transaction Risk Analysis
Examines ownership history and transaction relationships to flag potentially conflicting transfers, duplicate-sale scenarios, and other inconsistencies for further review.

### Mutation Workflow Tracking
Provides a structured view of mutation-related workflow stages and associated verification checks.

### Citizen Due Diligence
Supports preliminary checks of available ownership, mutation, tax, litigation, and other relevant land information before a proposed purchase.

### Cadastral Mapping and Public-Land Risk Indicators
Uses map-based visualization to present parcel boundaries and configured public-land or acquisition-related overlays where suitable data are available.

*These capabilities are subject to the current implementation, available datasets, and validation results. A flagged record is an indicator for review—not a definitive finding of fraud or legal status.*

## 4. Alignment with LandTech Problem Tracks

The project is designed around the six problem areas described in the LandTech Hackathon Rulebook.

| Track | Focus Area | Proposed Platform Contribution |
|---|---|---|
| P1 | Digitize Old Records | OCR-assisted extraction and structured presentation of legacy land-record information |
| P2 | Verify Deeds & Ownership | Digital document-integrity checks and verification support |
| P3 | Catch Fraud & Double-Selling | Rule-based analysis of potentially conflicting land transactions |
| P4 | Smart e-Mutation & Registry | Mutation workflow visibility and verification checkpoints |
| P5 | Check Before You Buy | Citizen-oriented preliminary land due diligence |
| P6 | Cadastral Boundary & Khas Protection | Map-based visualization of parcel boundaries and configured public-land risk indicators |

**Primary demonstration focus:** P3 — Catch Fraud & Double-Selling.

The final implementation status of each track should be confirmed against the corresponding code, test results, and demonstration evidence before submission.

## 5. System Overview

BHUMI-SYNC follows a modular architecture intended to separate the user interface, application logic, data storage, and verification workflows.

- **Presentation Layer:** Web-based interface for citizens, prospective buyers, and authorized reviewers.
- **Application Layer:** API endpoints, validation rules, authentication, authorization, and land-related business logic.
- **Data Layer:** Structured land-record datasets and relational persistence for the prototype.
- **Verification Layer:** Rule-based checks, document-integrity mechanisms, and risk indicators.
- **Mapping Layer:** Interactive geographic visualization of configured parcel and public-land layers.

This modular design provides a foundation for further testing, refinement, and potential integration with authorized information systems.

## 6. Technology Stack

The current project uses the following technologies where implemented:

- **Backend:** Python, FastAPI, Pydantic
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Mapping:** Leaflet and geographic data layers
- **Document Processing:** OCR tooling and digital document hashing
- **Testing:** Python automated tests and data-validation scripts

The exact dependencies and setup instructions are maintained in the project repository.

## 7. Prototype and Demonstration

**Current delivery:** Software prototype for local evaluation and controlled demonstration.

A public demonstration link will be added after the application has been deployed to an accessible hosting environment and its core workflows have been tested.

Until then, evaluators can review the source code, project documentation, test evidence, and locally demonstrated functionality.

**Repository:** https://github.com/nafis-ak/LandTechDeshMrittika

## 8. Data Governance, Security and Responsible Use

The prototype is intended to support responsible handling of land-related information. Its demonstration datasets should be clearly identified as synthetic or otherwise appropriately authorized.

Key principles include:

- No claim that synthetic records represent verified real-world ownership.
- No disclosure of personal or confidential land records without lawful authorization.
- Role-based access controls where implemented.
- Traceability of verification and review actions where supported.
- Human review of potential fraud indicators and conflicting records.
- Recognition of OCR limitations, incomplete records, and geographic-data uncertainty.
- No replacement of official records, legal procedures, or decisions by competent authorities.

Any future deployment within a government environment would require appropriate security assessment, authorized data access, legal review, operational testing, and institutional approval.

## 9. Current Scope and Future Development

Potential next steps include:

1. Complete implementation and regression testing of the core workflows.
2. Validate each problem-track requirement against documented acceptance criteria.
3. Improve the quality and traceability of synthetic-data validation.
4. Conduct security and access-control reviews.
5. Refine Bangla-language usability and accessibility.
6. Evaluate integration requirements with relevant authorized land-administration systems.
7. Prepare a controlled demonstration environment for external evaluation.

These items should be treated as future work until their completion is supported by evidence.

## 10. Team

**Team Name:** DeshMrittika

- **Team Leader:** Md. Asif Khandoker
- **Team Member:** Md. Saif Al Hasan

**Institution:** Daffodil International University (DIU)

## 11. Disclaimer

DeshMrittika / BHUMI-SYNC is an independently developed prototype intended for innovation, demonstration, and evaluation. It is not an official platform of the Ministry of Land or any other government authority.

All verification results are intended to support further examination and must not be interpreted as conclusive legal determinations. Any operational use would be subject to applicable laws, authorized data access, security requirements, and approval from the relevant authorities.

---

*DeshMrittika — Building a more transparent, traceable, and citizen-oriented land-information ecosystem for Bangladesh.*

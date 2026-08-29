# 🚀 SIH 2026 Project: Secure Digital Document Management System for Legal and Investigation Documents

[![SIH 2026](https://img.shields.io/badge/Smart%20India%20Hackathon-2026-blue.svg)](https://sih.gov.in)
[![Build Status](https://img.shields.io/badge/Status-In%20Development-green.svg)](#)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](#)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg?logo=react&logoColor=black)](#)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1.svg?logo=postgresql&logoColor=white)](#)

---

## 📌 Project Overview

* **Project Name:** Secure Digital Document Management System for Legal and Investigation Documents
* **Project Code:** 26190
* **Category:** Blockchain & Cybersecurity

### 📝 Project Description
As the volume of legal and investigation-related data continues to grow, there is an increasing need for a secure, centralized, and intelligent document management system that ensures data integrity, accessibility, confidentiality, and efficient case management. Modern technologies such as Cloud Computing, Artificial Intelligence (AI), Blockchain, Digital Signatures, and Secure Access Control can significantly improve the management and security of legal and investigative documents.

This project delivers a Secure Digital Document Management System (DMS) enabling law enforcement agencies, legal institutions, and investigative departments to securely store, organize, manage, retrieve, and share sensitive legal and investigation documents.

---

## ✨ Key Features

* **Digitized & Centralized Storage:** Centralized document repository with encrypted storage at rest.
* **Role-Based Access Control (RBAC):** Granular authorization and access control ensuring strict document confidentiality.
* **Tamper-Evident Integrity:** Immutable logging and cryptographic verification to prevent unauthorized modifications.
* **Complete Audit Trail:** Real-time tracking and logging of all document activities, access attempts, and edits.
* **Intelligent Search & Retrieval:** Indexed search functionality for rapid access to critical case files.
* **Collaborative & Secure Sharing:** Cross-department collaboration tools designed for legal and investigative workflows.
* **Regulatory Compliance:** Built to adhere to legal and regulatory data security standards.

---

## 👥 Team Members & Roles

| Name | Primary Role | Domain & Responsibilities |
| :--- | :--- | :--- |
| **Harshit Kumar** | 🌐 **Full Stack Development** | System integration, CI/CD, deployment infrastructure, container orchestration, and cross-tier feature bridging. |
| **Hansika** | 🎨 **Frontend Lead** | User interfaces, document viewers, role-based dashboards, and client-side security. |
| **Manas Roy** | ⚙️ **API Team** | REST API development, authentication, authorization, and storage engine implementation. |
| **Hrishit Khurana** | ⚙️ **API Team** | REST API development, authentication, authorization, and storage engine implementation. |
| **Akshat** | 💾 **Database Team** | Schema design, immutable logging, encryption at rest, and search indexing. |
| **Ansh Goyal** | 💾 **Database Team** | Schema design, immutable logging, encryption at rest, and search indexing. |

---

## 🛠️ Tech Stack & Tools

* **Frontend:** React + Vite + Tailwind CSS / JavaScript (ES Modules)
* **Backend API:** Python FastAPI + Uvicorn
* **Database:** PostgreSQL 15
* **DevOps & Infrastructure:** Docker, Docker Compose, GitHub Codespaces

---

## 🏗️ Project Architecture

```text
               ┌────────────────────────────────────────┐
               │        Client Browser (Vite UI)        │
               │         http://localhost:5173          │
               └───────────────────┬────────────────────┘
                                   │
                                   │ REST API Calls
                                   ▼
               ┌────────────────────────────────────────┐
               │       Python FastAPI Backend           │
               │         http://backend:8000            │
               └───────────────────┬────────────────────┘
                                   │
                                   │ SQL Queries
                                   ▼
               ┌────────────────────────────────────────┐
               │         PostgreSQL Database            │
               │         http://database:5432           │
               └────────────────────────────────────────┘

# Biology Problems OER

Explore **free and open problem sets** for Biochemistry, Genetics, and more! This repository hosts the content for [Biology Problems OER](https://biologyproblems.org), an open educational resource for students and educators.

---

## 🌐 Access the Website

Visit the live website here: **[https://biologyproblems.org](https://biologyproblems.org)**

---

## 📂 Repository Structure

This repository is structured to support the MkDocs framework with the Material theme. Here's an overview of the directory layout:

```
site_docs/
├── index.md                   # Main landing page
├── biochemistry/              # Biochemistry topics
│   ├── topic01/               # Topic 1
│   │   ├── index.md           # Topic 1 content
│   └── topic02/               # Topic 2
├── genetics/                  # Genetics topics
    ├── topic01/               # Topic 1
    │   ├── index.md           # Topic 1 content
    └── topic02/               # Topic 2
mkdocs.yml                     # Configuration for MkDocs
```

---

## 🚀 Local Development

To build and test the site locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/vosslab/biology-problems-website.git
   cd biology-problems-website
   ```

2. Install MkDocs and the Material theme:
   ```bash
   pip install mkdocs-material
   ```

3. Serve the site locally:
   ```bash
   mkdocs serve
   ```

4. Open your browser and visit `http://127.0.0.1:8000/`.

---

## 📦 Related Repositories

- **[Biology Problems Source Code](https://github.com/vosslab/biology-problems)**: The source code and problem sets are available in this repository. 

---

## 🛠️ Built With

- **[MkDocs](https://www.mkdocs.org/)**: A static site generator that's simple and fast.
- **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)**: A beautiful and customizable theme for MkDocs.

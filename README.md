# Generate Mini US Report Tutorial

This tutorial project show how to generate mini US report using [`LangChain`](https://python.langchain.com/v0.2/docs/introduction/) and `OpenAI` API.

## Setup

**OpenAI**

- Create `.env` file with `OPENAI_API_KEY` in the project root

```
OPENAI_API_KEY=your_api_key
```

**LangChain** (Optional)

- For LangSmith logging add the following to `.env`:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key
```

## Structure

This project structured as follows:

`prompt/`: contain prompts to feed into the context windows of LLM. Each separate markdown files will simply concatenate together to final prompt.

`abnormal/`: contain markdown document of abnormal findings. It will be build as **RAG** system.

`us_report_ext`: a custom Python package containing all of the functions needed to run this project. The Jupyter notebooks will shows how each function is build.


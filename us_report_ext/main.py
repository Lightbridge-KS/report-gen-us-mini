import itertools
from typing import Dict, List
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

from langchain_community.document_loaders import DirectoryLoader, TextLoader


from .findings import Findings
from ._utils import remove_duplicates, format_docs, read_markdown



def generate_report(user_input: str,
                    llm_main = ChatOpenAI(model="gpt-3.5-turbo"), # Main LLM for Prompt
                    llm_input = ChatOpenAI(model="gpt-3.5-turbo"), # LLM for instruct input
                    embedding = OpenAIEmbeddings(), 
                    ) -> str:
    # Get findings
    findings = get_findings(input_text=user_input, llm = llm_input)
    # Dict of Markdown Splits 
    md_header_splits_dict = load_split_md_docs("abnormal")
    # Dict of retrievers
    retriever_dict = get_chroma_retrievers(md_header_splits_dict, embedding= embedding)
    # Dict of Abnormal Docs 
    abn_doc_dict = retrieve_abnormal_docs(retriever_dict, findings)
    # Prompt Template
    prompt_temp = get_prompt_template(abn_doc_dict)
    
    rag_chain = (
        {"user": RunnablePassthrough()}  |
        prompt_temp | 
        llm_main | 
        StrOutputParser()
    )
    
    report = rag_chain.invoke(user_input)
    return report
    


def get_findings(input_text,
                 llm=ChatOpenAI(model="gpt-3.5-turbo")):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return `None` for the attribute's value.",
            ),
            # Please see the how-to about improving performance with
            # reference examples.
            # MessagesPlaceholder('examples'),
            ("human", "{input_text}"),
        ])

    runnable = prompt | llm.with_structured_output(schema=Findings)
    res = runnable.invoke({"input_text": input_text})
    return res



def load_split_md_docs(path: str) -> Dict[str, List[Document]]:
    """Load and Split Markdown Documents

    Args:
        path (str): path to folder containing markdown docs

    Returns:
        _dict_: Dictionary containing list of Documents
    """
    # Load all markdown files from `abnormal/` directory
    loader = DirectoryLoader(path = path, glob="**/*.md", loader_cls=TextLoader)
    docs_list = loader.load()
    
    ## Put into dictionary 
    docs_names = [Path(doc.metadata["source"]).stem for doc in docs_list]
    docs_dict = dict(zip(docs_names, docs_list))
    
    # Split
    ## Split Headings
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    ## MD splits
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )
    md_header_splits_dict = {name: markdown_splitter.split_text(doc.page_content) for name, doc in docs_dict.items()}
    return md_header_splits_dict




def get_chroma_retrievers(docs_splits_dict: Dict[str, List[Document]],
                          search_type: str = "similarity",
                          search_kwargs: Dict[str, any] = {"k": 3},
                          embedding = OpenAIEmbeddings()
                          ) -> Dict[str, VectorStoreRetriever]:

    chroma_dict = {name: Chroma.from_documents(docs_splits, embedding=embedding)
                   for name, docs_splits in docs_splits_dict.items()}

    retriever_dict = {
        name: chroma.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs)
        for name, chroma in chroma_dict.items()
    }

    return retriever_dict




def retrieve_abnormal_docs(retriever_dict: Dict[str, VectorStoreRetriever], findings: Findings) -> Dict[str, List[Document]]:
    
    out_dict = {}
    
    for key, retriever in retriever_dict.items():
        # Loop per organs
        query_list = findings.to_dict()[key]
        out_dict[key] = remove_duplicates(list(
            # Un-nest List
            itertools.chain(
                # Query for each item in findings
                *[retriever.invoke(f"Search only in the `metadata` field\n\nQuery: {query}") 
                for query in query_list]
            )
        ))
    
    return out_dict
    


def get_prompt_template(abnormal_doc_dict: Dict[str, List[Document]]):
    
    pr_text_intro = read_markdown("prompt/1_introduction.md")
    pr_text_eng = read_markdown("prompt/2_english_style_guide.md")
    pr_text_report_structure = read_markdown("prompt/3_report_structure.md")
    pr_text_temp_normal = read_markdown("prompt/4_report_template_normal.md")
    pr_text_temp_abn = read_markdown("prompt/5_abnormal.md")
    pr_abn_extracted = f"""

    liver:\n{format_docs(abnormal_doc_dict["abnormal_liver"])}

    kidney:\n{format_docs(abnormal_doc_dict["abnormal_kidney"])}

    gallbladder:\n{format_docs(abnormal_doc_dict["abnormal_gallbladder"])}
    """

    # Join them
    pr_text = "\n\n".join([pr_text_intro, pr_text_eng,
                        pr_text_report_structure, pr_text_temp_normal, 
                        pr_text_temp_abn, pr_abn_extracted]) 


    prompt = "\n\n".join([pr_text,
                """
    User input: {user}

    Output:
    """])

    prompt_temp = ChatPromptTemplate.from_template(prompt)
    return prompt_temp
    
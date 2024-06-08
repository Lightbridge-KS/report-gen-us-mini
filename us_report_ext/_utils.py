# Helper Function

def remove_duplicates(objects):
    unique_objects = []
    for obj in objects:
        if obj not in unique_objects:
            unique_objects.append(obj)
    return unique_objects


def read_markdown(path):
    """
    Read a markdown file from a given file path and return the content as a string.

    Args:
    path (str): The file path to the markdown file.

    Returns:
    str: The content of the markdown file as a string.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "The file could not be found."
    except Exception as e:
        return f"An error occurred: {e}"


def format_docs(docs):
    if docs == []:
        return ""
    else:
        return "\n\n".join(doc.page_content for doc in docs)
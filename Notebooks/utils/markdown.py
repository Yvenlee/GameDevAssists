import re
def clean_markdown(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"#+\s?", "", text)
    text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text)
    return text

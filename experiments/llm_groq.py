# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     temperature=0.3,
# )

# response = llm.invoke([
#     HumanMessage(content="What is deep learning")
# ])

# print(response.content)




















# from dotenv import load_dotenv
# import os
# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage

# # Load .env file
# load_dotenv()

# # Verify key is loaded
# api_key = os.getenv("GROQ_API_KEY")

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     temperature=0.3,
#     api_key=api_key
# )

# response = llm.invoke([
#     HumanMessage(content="What is data scientist. Explain step by step.")
# ])

# print(response.content)

















import streamlit as st
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

st.title("Groq LLM Test (LangChain + Streamlit)")

if not api_key:
    st.error("GROQ_API_KEY not found. Please set it in your .env file.")
else:
    llm = ChatGroq(
        model="openai/gpt-oss-120b", # openai/gpt-oss-120b, llama-3.1-8b-instant
        temperature=0.3,
        api_key=api_key
    )

    # ✅ Single-line input box
    user_input = st.text_area(
        "Enter your prompt:",
        value="What is a data scientist? Explain step by step."
    )

    if st.button("Run LLM"):
        if not user_input.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Thinking..."):
                response = llm.invoke([
                    HumanMessage(content=user_input)
                ])

            st.subheader("Response:")
            st.write(response.content)











# Generate google style, numpy style, rest style docstring, for below code. and give same code which includes docstring.

# please follow this structure:

#     """
#     Short description of `add`.

#     Args:
#         a (int): DESCRIPTION.
#         b (int): DESCRIPTION.

#     Returns:
#         int: DESCRIPTION.
#     """

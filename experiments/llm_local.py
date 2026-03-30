# from langchain_community.llms import LlamaCpp
# from langchain_core.prompts import PromptTemplate

# MODEL_PATH = r"D:\Mentor\LLM_MODELS\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

# # Load model
# llm = LlamaCpp(
#     model_path=MODEL_PATH,
#     n_ctx=2048,
#     n_threads=8,
#     n_gpu_layers=0,
#     temperature=0.3
# )

# # Create a prompt template
# prompt = PromptTemplate.from_template(
#     "You are a helpful AI teacher.\n\nQuestion: {question}\n\nAnswer step by step:"
# )

# # ✔️ New LangChain pipeline style
# chain = prompt | llm

# # Run the chain
# response = chain.invoke({"question": "What is AI?"})

# print(response)















import streamlit as st
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate

MODEL_PATH = r"D:\Mentor\LLM_MODELS\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

st.title("Local Llama 3.1 (8B) - GGUF Chatbot")


# ---------- Cached model loader (global, reused across sessions) ----------
@st.cache_resource
def load_model():
    # Don't print or write here -> avoids "loading" message every rerun
    return LlamaCpp(
        model_path=MODEL_PATH,
        n_ctx=8192, # 2048, 4096, 8192
        n_threads=8,
        n_gpu_layers=0,
        temperature=0.3,
    )


# ---------- Session state init ----------
if "llm" not in st.session_state:
    st.session_state.llm = None
    st.session_state.model_loaded = False


# ---------- UI: Load button ----------
if not st.session_state.model_loaded:
    st.info("Click the button to load the model (first time only).")

    if st.button("Load model"):
        with st.spinner("Loading model... this may take some time the first run."):
            st.session_state.llm = load_model()
        st.session_state.model_loaded = True
        st.success("✅ Model loaded!")
        st.rerun()
else:
    st.success("✅ Model loaded! You can ask questions.")

    llm = st.session_state.llm

    # Prompt template + chain
    prompt = PromptTemplate.from_template(
        "You are a helpful AI.\nQuestion: {question}\nAnswer:"
    )
    chain = prompt | llm

    # Single-line input
    user_input = st.text_input("Enter your question:", "")

    if st.button("Send"):
        if not user_input.strip():
            st.warning("Please enter a question!")
        else:
            with st.spinner("Thinking..."):
                result = chain.invoke({"question": user_input})
            st.subheader("Response:")
            st.write(result)



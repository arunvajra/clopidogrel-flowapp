import streamlit as st
import csv
import ast  # Used for safely evaluating strings as Python expressions

def load_csv_as_dict(filename, key_column, value_columns):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return {row[key_column]: {key: ast.literal_eval(row[key]) if key in ['answers', 'next'] else row[key] for key in value_columns} for row in reader}

questions = load_csv_as_dict("questions.csv", "id", ["label", "answers", "next"])
prompts = load_csv_as_dict("prompts.csv", "id", ["label", "action"])

def get_next_step(current_step, answer):
    answer_index = current_step["answers"].index(answer)
    next_step_str = current_step["next"][answer_index]
    next_type, next_id = next_step_str.split(":")
    return next_type, next_id

def create_message_bubble(text, is_question=True):
    bubble_color = "#E0E0E0" if is_question else "#B3E5FC"
    text_color = "#000000"
    align = "left" if is_question else "right"
    markdown = f"""
    <style>
    .bubble {{
        background: {bubble_color};
        border-radius: 20px;
        padding: 10px;
        color: {text_color};
        text-align: {align};
        display: inline-block;
        max-width: 70%;
    }}
    </style>
    <div class="bubble">
        {text}
    </div>
    """
    st.markdown(markdown, unsafe_allow_html=True)

def show_step(step_id):
    step_type, step_index = step_id.split(":")
    if step_type == "question":
        question = questions.get(step_index)
        if question is None:
            st.error(f"Question with ID {step_index} not found.")
            return

        create_message_bubble(question["label"])

        cols = st.columns(len(question["answers"]))
        for i, answer in enumerate(question["answers"]):
            with cols[i]:
                button_key = f"{answer}_{step_index}"
                if st.button(answer, key=button_key):
                    next_type, next_id = get_next_step(question, answer)
                    st.session_state.next_step = f"{next_type}:{next_id}"
                    return

    elif step_type == "prompt":
        prompt = prompts.get(step_index)
        if prompt is None:
            st.error(f"Prompt with ID {step_index} not found.")
            return

        create_message_bubble(prompt["label"], is_question=False)
        st.session_state.next_step = None
        return

def main():
    st.set_page_config(page_title="Medical Decision Support System", layout="wide")
    
    with st.sidebar:
        st.title("Navigation")
        if st.button("Restart"):
            st.session_state.current_step = "question:1"

    st.title("Medical Decision Support System")

    if "current_step" not in st.session_state:
        st.session_state.current_step = "question:1"
    if "next_step" not in st.session_state:
        st.session_state.next_step = None

    show_step(st.session_state.current_step)

    if "next_step" in st.session_state and st.session_state.next_step is not None:
        st.session_state.current_step = st.session_state.next_step
        st.session_state.next_step = None
        show_step(st.session_state.current_step)

if __name__ == "__main__":
    main()


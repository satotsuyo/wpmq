import streamlit as st
import time
import random
import re

# ------------------------------
# 問題生成用の関数群
# ------------------------------
def modify_sentence(sentence, make_false=False):
    """
    文の意味を反転させるために "not" を適切に挿入する
    """
    if make_false:
        markers = [" is ", " are ", " was ", " were ", " can ", " should ", " will "]
        for marker in markers:
            if marker in sentence:
                parts = sentence.split(marker)
                if len(parts) > 1:
                    return parts[0] + marker.strip() + " not " + parts[1]
        return sentence  # 変更できない場合はそのまま返す
    else:
        return sentence  # True文（変更しない）

def generate_comprehension_questions(text, num=4):
    """
    True/False形式の読解問題を生成（Falseは意味を反転）
    """
    # 正規表現でピリオド区切り
    sentences = [s.strip() for s in re.split(r'\.\s*', text) if s.strip()]
    if not sentences:
        sentences = [text]

    selected_sentences = random.sample(sentences, min(num, len(sentences)))

    questions = []
    for sentence in selected_sentences:
        if any(marker in sentence for marker in [" is ", " are ", " was ", " were ", " can ", " should ", " will "]):
            make_false = True
        else:
            make_false = False

        if make_false:
            question_statement = modify_sentence(sentence, make_false=True)
            correct_answer = "False"
        else:
            question_statement = modify_sentence(sentence, make_false=False)
            correct_answer = "True"

        questions.append({
            "question": question_statement,
            "correct_answer": correct_answer
        })

    return questions

# ------------------------------
# セッションステートの初期化
# ------------------------------
if 'finished' not in st.session_state:
    st.session_state.finished = False
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'wpm' not in st.session_state:
    st.session_state.wpm = None
if 'questions' not in st.session_state:
    st.session_state.questions = None

# タイトル表示
st.markdown("""
    <h1 style='text-align: center; font-size: 3.0em;'>
        CompRateWPM <br>（Comprehension × WPM）
    </h1>
""", unsafe_allow_html=True)

# 使い方の説明
st.markdown("""
**使い方**
- 読む英文を入力してください。
- 「リーディング開始」ボタンを押すと、時間の計測が始まります。
- 読み終えたら、「内容理解テストに進む」ボタンを押してください。
  - 読んだ英文に関する〇×問題（4問）が出題されます。
- テストを終えて「スコアを表示」ボタンを押すと、
  - WPM（1分あたりの語数）に正答率をかけたスコアが表示されます。
""", unsafe_allow_html=True)

# ------------------------------
# 読書フェーズ
# ------------------------------
with st.container():
    col1, col2 = st.columns([4, 1])

    with col1:
        if not st.session_state.finished:
            st.session_state.input_text = st.text_area("読む英文を入力してください", height=400)
        else:
            st.write("パッセージは非表示です。")

    with col2:
        # 「リーディング開始」ボタンは常に表示
        if st.button("リーディング開始", key="start") and st.session_state.start_time is None:
            if st.session_state.input_text.strip():
                st.write("読み始めます。読み終えたら「内容理解テストに進む」を押してください。")
                st.session_state.start_time = time.time()
            else:
                st.warning("まず英文を入力してください。")

        if st.session_state.input_text:
            cleaned_text = re.sub(r'[,:;"\'.]', '', st.session_state.input_text)
            words = cleaned_text.split()
            total_words = len(words)

            st.markdown(f"総語数: <b style='font-size: 1.5em;'>{total_words}</b>", unsafe_allow_html=True)

            if st.session_state.start_time is not None:
                if st.button("内容理解テストに進む", key="finish"):
                    end_time = time.time()
                    reading_time_minutes = (end_time - st.session_state.start_time) / 60

                    if reading_time_minutes < 0.05:
                        st.warning("読了時間が短すぎます。再度お試しください。")
                    else:
                        st.session_state.wpm = total_words / reading_time_minutes
                        st.markdown(f"読了時間: <b style='font-size: 1.5em;'>{round(reading_time_minutes, 2)}</b> 分", unsafe_allow_html=True)
                        st.markdown(f"WPM: <b style='font-size: 1.5em;'>{round(st.session_state.wpm, 2)}</b>", unsafe_allow_html=True)
                        st.session_state.finished = True
                        st.write("読了しました。以下に内容理解問題を提示します。")

# ------------------------------
# 問題＆スコア表示
# ------------------------------
if st.session_state.finished and st.session_state.input_text and st.session_state.wpm is not None:
    st.write("以下の内容理解問題にお答えください。（True/False を選択）")

    if st.session_state.questions is None:
        st.session_state.questions = generate_comprehension_questions(st.session_state.input_text, num=4)

    user_answers = []
    for idx, q in enumerate(st.session_state.questions):
        st.write(f"Q{idx+1}: {q['question']}")
        ans = st.radio(f"Q{idx+1} の解答", ("True", "False"), key=f"q{idx}")
        user_answers.append(ans)

    if st.button("スコアを表示"):
        correct_count = sum(1 for idx, q in enumerate(st.session_state.questions) if user_answers[idx] == q['correct_answer'])
        accuracy = correct_count / len(st.session_state.questions)
        final_score = st.session_state.wpm * accuracy

        st.markdown(f"正答率: <b style='font-size: 1.5em;'>{accuracy * 100:.2f}%</b>", unsafe_allow_html=True)
        st.markdown(f"最終スコア（WPM × 正答率）: <b style='font-size: 1.5em;'>{final_score:.2f}</b>", unsafe_allow_html=True)

        # 正答表示
        st.markdown("---")
        st.subheader("各問題の正解")
        for idx, q in enumerate(st.session_state.questions):
            st.write(f"Q{idx+1}: {q['question']}")
            st.markdown(f"<span style='color: green;'>正解: {q['correct_answer']}</span>", unsafe_allow_html=True)

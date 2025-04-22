import streamlit as st
import time
import random

# ------------------------------
# 問題生成用の関数群
# ------------------------------
def modify_sentence(sentence, make_false=False):
    """
    文章の意味を確実に反転させるために "not" を適切に挿入する。
    """
    if make_false:
        markers = [" is ", " are ", " was ", " were ", " can ", " should ", " will "]
        for marker in markers:
            if marker in sentence:
                parts = sentence.split(marker)
                if len(parts) > 1:
                    return parts[0] + marker + "not " + parts[1]
        return sentence  # 不要な "not added" 表示を削除
    else:
        return sentence

def generate_comprehension_questions(text, num=4):
    """
    重複を避け、確実に True/False の問題を作成する
    """
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if not sentences:
        sentences = [text]

    selected_sentences = random.sample(sentences, min(num, len(sentences)))

    questions = []
    for sentence in selected_sentences:
        # Falseを作る場合、確実に変更できるかチェック
        if any(marker in sentence for marker in [" is ", " are ", " was ", " were ", " can ", " should ", " will "]):
            make_false = True
        else:
            make_false = False  # 文が変更できない場合はTrueのままにする

        if make_false:
            question_statement = modify_sentence(sentence, make_false=True)
            correct_answer = "False"
        else:
            question_statement = sentence
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

# ------------------------------
# タイトル表示（フォントサイズ拡大）
# ------------------------------
st.markdown("""
    <h1 style='text-align: center; font-size: 2.0em;'>
        CompRateWPM <br>（Comprehension × WPM）
    </h1>
""", unsafe_allow_html=True)

# ------------------------------
# 使い方の説明（タイトルのみ太字）
# ------------------------------
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
# 「読書フェーズ」コンテナ
# ------------------------------
with st.container():
    col1, col2 = st.columns([4, 1])

    with col1:
        st.session_state.input_text = st.text_area("読む英文を入力してください", height=400)

    with col2:
        st.button("リーディング開始", key="start")  # 最初からボタンを表示

        if st.session_state.start_time is None:
            if st.session_state.input_text:
                st.write("読み始めます。読み終わったら右側の「内容理解テストに進む」ボタンを押してください。")
                st.session_state.start_time = time.time()
            else:
                st.write("英文を入力してください。")  # 入力前に押した場合のメッセージ

# ------------------------------
# 内容理解問題とスコア表示
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
        accuracy = correct_count / 4
        final_score = st.session_state.wpm * accuracy

        st.markdown(f"正答率: <b style='font-size: 1.5em;'>{accuracy * 100:.2f}%</b>", unsafe_allow_html=True)
        st.markdown(f"最終スコア（WPM × 正答率）: <b style='font-size: 1.5em;'>{final_score:.2f}</b>", unsafe_allow_html=True)

        # 各問題の正解を表示
        st.markdown("---")
        st.subheader("各問題の正解")
        for idx, q in enumerate(st.session_state.questions):
            st.write(f"Q{idx+1}: {q['question']}")
            st.markdown(f"<span style='color: green;'>正解: {q['correct_answer']}</span>", unsafe_allow_html=True)

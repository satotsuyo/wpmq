import streamlit as st
import time
import random
import re

# 形容詞とその反意語のペア
adjective_antonyms = {
    "good": "bad",
    "many": "few",
    "big": "small",
    "happy": "sad",
    "easy": "hard",
    "fast": "slow",
    "hot": "cold",
    "strong": "weak",
    "rich": "poor",
    "bright": "dark",
    "young": "old",
    "clean": "dirty",
    "safe": "dangerous",
    "short": "long",
    "strong": "weak",
    "near": "far",
    "expensive": "cheap",
    "hard": "soft",
    "heavy": "light",
    "new": "old",
    "smart": "stupid",
    "tall": "short",
    "long": "short",
    "beautiful": "ugly",
    "rich": "poor",
    "quiet": "noisy",
    "slow": "fast",
    "weak": "strong",
    "funny": "serious",
    "clean": "dirty",
    "interesting": "boring",
    "bright": "dim",
    "friendly": "unfriendly",
    "polite": "impolite",
    "brave": "cowardly",
    "thin": "fat",
    "active": "lazy",
    "fresh": "stale",
    "modern": "ancient",
    "healthy": "unhealthy",
    "soft": "hard",
    "warm": "cold",
    "quiet": "loud",
    "sharp": "blunt",
    "rich": "poor",
    "peaceful": "violent",
    "beautiful": "ugly",
    "quiet": "loud",
}

# ------------------------------
# 文の修正関数（False文生成）
# ------------------------------
def modify_sentence(sentence, make_false=False):
    if not make_false:
        return sentence

    # False文生成の方法をランダムに選択
    method = random.choice(['negation', 'number_change', 'adjective_antonym'])

    if method == 'negation':
        patterns = [
            (r'\b(is|are|was|were|can|should|will)\b', r'\1 not'),
            (r'\bThere(is|are)\b', r'There \1 not'),
            (r'\bIt(is)\b', r'It \1 not'),
            (r'\bThat(is)\b', r'That \1 not')
        ]
        for pattern, replacement in patterns:
            new_sentence = re.sub(pattern, replacement, sentence)
            if new_sentence != sentence:
                return new_sentence

    elif method == 'number_change':
        number_matches = re.findall(r'\d+', sentence)
        if number_matches:
            num_to_replace = random.choice(number_matches)
            new_num = str(int(num_to_replace) + random.choice([1, 2, 3, 5, 10]))
            return sentence.replace(num_to_replace, new_num, 1)

    elif method == 'adjective_antonym':
        # 形容詞の反意語に置き換える
        words = sentence.split()
        for i, word in enumerate(words):
            if word in adjective_antonyms:
                words[i] = adjective_antonyms[word]
        return ' '.join(words)

    return sentence  # 変更できなければ元の文を返す

# ------------------------------
# 問題生成関数
# ------------------------------
def generate_comprehension_questions(text, num=4):
    sentences = [s.strip() for s in re.split(r'\.\s*', text) if s.strip()]
    if not sentences:
        sentences = [text]

    selected_sentences = random.sample(sentences, min(num, len(sentences)))

    questions = []
    for sentence in selected_sentences:
        make_false = any(word in sentence for word in [" is", " are", " was", " were", " can", " should", " will", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        question_statement = modify_sentence(sentence, make_false)
        correct_answer = "False" if question_statement != sentence else "True"

        questions.append({
            "question": question_statement,
            "correct_answer": correct_answer
        })

    return questions

# ------------------------------
# セッション初期化
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
# タイトルと説明
# ------------------------------
st.markdown("<h1 style='text-align: center;'>CompRateWPM（Comprehension × WPM）</h1>", unsafe_allow_html=True)

st.markdown(""" 
**使い方**
- 読む英文を入力してください。
- 「リーディング開始」ボタンを押すと時間が計測されます。
- 読み終えたら「内容理解テストに進む」ボタンで〇×問題に進めます。
""")

# ------------------------------
# 入力とボタン
# ------------------------------
with st.container():
    col1, col2 = st.columns([4, 1])

    with col1:
        if not st.session_state.finished:
            st.session_state.input_text = st.text_area("読む英文を入力してください", height=400)
        else:
            st.write("パッセージは非表示です。")

    with col2:
        if st.button("リーディング開始", key="start") and st.session_state.start_time is None:
            if st.session_state.input_text.strip():
                st.session_state.start_time = time.time()
            else:
                st.warning("まず英文を入力してください。")

        if st.session_state.input_text:
            cleaned_text = re.sub(r'[,:;"\'.]', '', st.session_state.input_text)
            total_words = len(cleaned_text.split())
            st.markdown(f"総語数: <b>{total_words}</b>", unsafe_allow_html=True)

            if st.session_state.start_time is not None:
                if st.button("内容理解テストに進む", key="finish"):
                    end_time = time.time()
                    reading_time_minutes = (end_time - st.session_state.start_time) / 60

                    if reading_time_minutes < 0.05:
                        st.warning("読了時間が短すぎます。再度お試しください。")
                    else:
                        st.session_state.wpm = total_words / reading_time_minutes
                        st.session_state.finished = True

# ------------------------------
# WPMと問題とスコア
# ------------------------------
if st.session_state.finished and st.session_state.input_text and st.session_state.wpm:
    st.markdown(f"WPM: <b>{round(st.session_state.wpm, 2)}</b>", unsafe_allow_html=True)

    if st.session_state.questions is None:
        st.session_state.questions = generate_comprehension_questions(st.session_state.input_text)

    st.subheader("内容理解問題")

    user_answers = []
    for idx, q in enumerate(st.session_state.questions):
        st.write(f"Q{idx+1}: {q['question']}")
        ans = st.radio("", ("True", "False"), key=f"q{idx}")  # ラベルを空に
        user_answers.append(ans)

    if st.button("スコアを表示"):
        correct = sum(1 for i, q in enumerate(st.session_state.questions) if user_answers[i] == q['correct_answer'])
        accuracy = correct / len(st.session_state.questions)
        score = st.session_state.wpm * accuracy

        st.markdown(f"正答率: <b>{accuracy*100:.2f}%</b>", unsafe_allow_html=True)
        st.markdown(f"スコア（WPM×正答率）: <b>{score:.2f}</b>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("---")
        st.subheader("正解一覧")

        for i, q in enumerate(st.session_state.questions):
            result = "✅" if user_answers[i] == q['correct_answer'] else "❌"
            st.write(f"{result} Q{i+1}: {q['question']}（正解: {q['correct_answer']} / あなたの解答: {user_answers[i]}）")

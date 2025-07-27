import streamlit as st
import requests
import urllib.parse
import os

st.set_page_config(page_title="LINE OAuth Demo", page_icon="✅")

# --- シークレットから読み込む ---
CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"]
REDIRECT_URI = st.secrets["redirect_uri"]

# --- クエリパラメータを取得（LINE認証後の code を含む） ---
query_params = st.query_params
code = query_params.get("code", [None])[0]
state = query_params.get("state", [None])[0]

# --- トップページ（ログイン前） ---
if code is None:
    st.title("LINEログインデモ")

    line_auth_url = "https://access.line.me/oauth2/v2.1/authorize"
    query = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "streamlitdemo123",
        "scope": "profile openid email",
        "prompt": "consent"
    }
    login_url = f"{line_auth_url}?{urllib.parse.urlencode(query)}"

    st.markdown(f"""
    [![LINEでログイン](https://scdn.line-apps.com/n/line_add_friends/btn/ja.png)]({login_url})
    """)
    st.info("上のボタンを押して、LINEログインを試してください。")
else:
    # --- アクセストークンの取得 ---
    token_url = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    token_res = requests.post(token_url, headers=headers, data=data)
    token_json = token_res.json()

    if "access_token" not in token_json:
        st.error("アクセストークンの取得に失敗しました")
        st.json(token_json)
    else:
        access_token = token_json["access_token"]
        # --- ユーザー情報の取得 ---
        profile_url = "https://api.line.me/v2/profile"
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_res = requests.get(profile_url, headers=headers)
        profile_json = profile_res.json()

        # --- 表示 ---
        st.success("LINEログイン成功！")
        st.image(profile_json["pictureUrl"], width=100)
        st.write(f"ようこそ、{profile_json['displayName']} さん！")
        st.code(profile_json)

from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量

load_dotenv()

app = Flask(__name__)

# 飞书API配置
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET')
FEISHU_TABLE_ID = os.getenv('FEISHU_TABLE_ID')
FEISHU_SHEET_ID = os.getenv('FEISHU_SHEET_ID')

 

# 获取飞书访问令牌
def get_feishu_token():
    print("获取飞书Token..."+FEISHU_APP_ID+FEISHU_APP_SECRET)

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    token_data = response.json()
    print("获取的飞书Token数据:", json.dumps(token_data, ensure_ascii=False, indent=2))
    return token_data.get("tenant_access_token")

# 从飞书多维表格获取博客数据
def get_blog_data():
    token = get_feishu_token()
    print(f"使用的Token: {token}")
    
    # 使用 Base API 获取数据
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/CdeNbqKlFaSrBhshuQycurHinBd/tables/{FEISHU_TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    print("从飞书获取的数据:", json.dumps(data, ensure_ascii=False, indent=2))
    
    # 处理返回的数据结构
    records = data.get("data", {}).get("items", [])
    blog_posts = []
    
    for i, record in enumerate(records, 1):
        fields = record.get("fields", {})
        blog_post = {
            "id": i,
            "title": fields.get("标题", ""),
            "quote": fields.get("金句输出", ""),
            "comment": fields.get("点评内容", ""),
            "content": fields.get("全文内容提取", ""),
        }
        blog_post["preview"] = blog_post["content"][:100] + "..." if len(blog_post["content"]) > 100 else blog_post["content"]
        blog_posts.append(blog_post)
    
    return blog_posts

@app.route('/')
def index():
    blog_posts = get_blog_data()
    return render_template('index.html', blog_posts=blog_posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    blog_posts = get_blog_data()
    post = next((p for p in blog_posts if p["id"] == post_id), None)
    if post:
        return render_template('post.html', post=post)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
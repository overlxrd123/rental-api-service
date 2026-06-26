# -*- coding: utf-8 -*-
import os, shutil, urllib.request

from flask import Flask, jsonify
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io, base64

# === 中文字体：直接下载字体文件，不依赖系统字体 ===
FONT_PATH = os.path.join(os.path.dirname(__file__), 'NotoSansSC.ttf')
FONT_URL = 'https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf'

if not os.path.exists(FONT_PATH):
    print('下载中文字体文件...')
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        print('字体下载成功')
    except:
        print('字体下载失败，尝试系统字体')

if os.path.exists(FONT_PATH):
    fm.fontManager.addfont(FONT_PATH)
    font_prop = fm.FontProperties(fname=FONT_PATH)
    font_name = font_prop.get_name()
    plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    print(f'使用字体: {font_name}')
else:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    print('警告：无中文字体')

plt.rcParams['axes.unicode_minus'] = False

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False  # 新版 Flask 双重保险

try:
    df = pd.read_csv('lianjia_bj_rent.csv', encoding='gbk')
except:
    df = pd.read_csv('lianjia_bj_rent.csv', encoding='utf-8')
print(f'数据加载完成，共 {len(df)} 条房源')

@app.route('/')
def home():
    return '<!DOCTYPE html>\n<html lang="zh-CN">\n<head><meta charset="utf-8"><title>北京租房数据分析 API</title></head>\n<body>\n<h1>北京租房数据分析 API</h1>\n<p>数据来源：链家实时爬取</p>\n<ul>\n<li><a href="/api/avg_price">/api/avg_price</a> — 各区平均租金（JSON）</li>\n<li><a href="/api/stats">/api/stats</a> — 整体统计（JSON）</li>\n<li>/api/district/海淀 — 查看某个区的房源</li>\n<li><a href="/chart">/chart</a> — 租金分布图表</li>\n</ul>\n</body></html>'

@app.route('/api/avg_price')
def avg_price():
    result = df.groupby('区')['价格_元'].agg(['count', 'mean', 'min', 'max']).round(1)
    result.columns = ['房源数', '均价', '最低', '最高']
    return jsonify(result.to_dict(orient='index'))

@app.route('/api/stats')
def stats():
    return jsonify({
        '房源总数': len(df),
        '北京均价': round(df['价格_元'].mean(), 1),
        '价格中位数': round(df['价格_元'].median(), 1),
        '最贵区域': df.groupby('区')['价格_元'].mean().idxmax(),
        '最便宜区域': df.groupby('区')['价格_元'].mean().idxmin()
    })

@app.route('/api/district/<name>')
def district(name):
    data = df[df['区'] == name]
    if len(data) == 0:
        return jsonify({'error': 'no data'}), 404
    return jsonify(data[['价格_元', '面积', '户型', '描述']].head(20).to_dict(orient='records'))

@app.route('/chart')
def chart():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    d_price = df.groupby('区')['价格_元'].mean().round(0).sort_values(ascending=False).head(8)
    axes[0].barh(d_price.index[::-1], d_price.values[::-1], color='#2b5c9e')
    axes[0].set_title('各区平均租金')
    axes[0].set_xlabel('元/月')
    axes[1].hist(df['价格_元'], bins=20, color='#DD8452', edgecolor='white')
    axes[1].set_title('租金分布')
    axes[1].set_xlabel('月租金')
    axes[1].set_ylabel('房源数')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode()
    buf.close()
    plt.close()
    return '<!DOCTYPE html>\n<html lang="zh-CN">\n<head><meta charset="utf-8"><title>图表</title></head>\n<body>\n<h2>北京租房分析图表</h2>\n<img src="data:image/png;base64,' + img + '">\n</body></html>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

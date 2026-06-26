# -*- coding: utf-8 -*-
import os, shutil, urllib.request

# 自动安装中文字体（Linux/Render 环境）
if os.name != 'nt':
    os.system('apt-get update -qq && apt-get install -y -qq fonts-noto-cjk 2>/dev/null')
    # 清除 matplotlib 字体缓存，否则新字体不生效
    cache_dir = os.path.expanduser('~/.cache/matplotlib')
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir, ignore_errors=True)

from flask import Flask, jsonify
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io, base64

# 中文字体配置：重建字体列表
fm._load_fontmanager(try_read_cache=False)

font_list = ['Noto Sans CJK SC', 'Noto Sans SC', 'WenQuanYi Micro Hei', 'SimHei', 'Microsoft YaHei']
available = [f.name for f in fm.fontManager.ttflist]
chosen = None
for f in font_list:
    if f in available:
        chosen = f
        break

if chosen:
    plt.rcParams['font.sans-serif'] = [chosen, 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
else:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False
print(f'字体: {chosen or "警告-无中文字体"}')

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

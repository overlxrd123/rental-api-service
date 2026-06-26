"""
数据分析 API 服务
用 Flask 把 Pandas 分析能力变成网页接口
"""
from flask import Flask, jsonify, render_template_string
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 不用弹窗，直接保存图片
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# 启动时加载数据
df = pd.read_csv('lianjia_bj_rent.csv', encoding='gbk')
print(f"数据加载完成，共 {len(df)} 条房源")

# ===== 路由 1：首页 =====
@app.route('/')
def home():
    return '''
    <h1>🏠 北京租房数据分析 API</h1>
    <p>数据来源：链家实时爬取</p>
    <ul>
        <li><a href="/api/avg_price">/api/avg_price</a> — 各区平均租金</li>
        <li><a href="/api/stats">/api/stats</a> — 整体统计</li>
        <li>/api/district/海淀 — 查看某个区的房源</li>
        <li><a href="/chart">/chart</a> — 租金分布图</li>
    </ul>
    '''

# ===== 路由 2：各区平均租金（JSON API）=====
@app.route('/api/avg_price')
def avg_price():
    result = df.groupby('区')['价格_元'].agg(['count', 'mean', 'min', 'max']).round(1)
    result.columns = ['房源数', '均价', '最低', '最高']
    return jsonify(result.to_dict(orient='index'))

# ===== 路由 3：整体统计 =====
@app.route('/api/stats')
def stats():
    return jsonify({
        '房源总数': len(df),
        '北京均价': round(df['价格_元'].mean(), 1),
        '价格中位数': round(df['价格_元'].median(), 1),
        '最贵区域': df.groupby('区')['价格_元'].mean().idxmax(),
        '最便宜区域': df.groupby('区')['价格_元'].mean().idxmin()
    })

# ===== 路由 4：查某个区（动态路由）=====
@app.route('/api/district/<name>')
def district(name):
    data = df[df['区'] == name]
    if len(data) == 0:
        return jsonify({'error': f'没有找到"{name}"的数据'}), 404
    return jsonify(data[['价格_元', '面积', '户型', '描述']].head(20).to_dict(orient='records'))

# ===== 路由 5：生成图表 =====
@app.route('/chart')
def chart():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # 各区均价柱状图
    d_price = df.groupby('区')['价格_元'].mean().round(0).sort_values(ascending=False).head(8)
    axes[0].barh(d_price.index[::-1], d_price.values[::-1], color='#2b5c9e')
    axes[0].set_title('北京各区平均租金')
    axes[0].set_xlabel('元/月')

    # 租金分布直方图
    axes[1].hist(df['价格_元'], bins=20, color='#DD8452', edgecolor='white')
    axes[1].set_title('租金分布')
    axes[1].set_xlabel('月租金（元）')
    axes[1].set_ylabel('房源数')

    plt.tight_layout()

    # 图片转 base64，直接嵌入网页
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    buf.close()

    return f'<h2>北京租房数据分析图表</h2><img src="data:image/png;base64,{img_base64}">'

# ===== 启动 =====
if __name__ == '__main__':
    app.run(debug=True, port=5000)

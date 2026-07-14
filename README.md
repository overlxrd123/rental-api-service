# 租房数据分析 API 服务 — Flask + Render 云部署

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-lightgrey)
![Status](https://img.shields.io/badge/deployed-online-green)

将 Pandas 数据分析能力封装为 RESTful API，通过 Render 部署上线，全球可访问。

## 🔗 在线地址

https://rental-api-service.onrender.com

## 📡 API 接口

| 接口 | 功能 |
|------|------|
| `/` | 首页导航 |
| `/api/avg_price` | 各区平均租金（JSON） |
| `/api/stats` | 整体统计指标 |
| `/api/district/<name>` | 动态路由查指定区域 |
| `/chart` | Matplotlib 生成图表嵌入网页 |

## 🛠 技术栈

`Python` `Flask` `Pandas` `Matplotlib` `Render` `RESTful API`

## ▶️ 本地运行

```bash
pip install flask pandas matplotlib
python app.py
```

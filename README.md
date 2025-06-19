# CSGOSkinAnalyzer

## 项目简介
本项目用于聚合多平台CSGO饰品市场数据，分析饰品是否值得购入，并以图形界面展示分析结果。

## 使用方法

1. 安装依赖（建议使用Python 3.8+）：
   ```
   pip install -r requirements.txt
   ```

2. 配置API密钥  
   编辑 `config/settings.py`，填写你的API密钥。

3. 启动程序
   ```
   python main.py
   ```

4. 在界面输入饰品链接，点击“分析”即可获取分析结果。

## 打包为exe
推荐使用 PyInstaller：
```
pip install pyinstaller
pyinstaller -F -w main.py
```
生成的 `dist/main.exe` 即为便携版。

## 依赖
- PyQt5
- requests
- numpy
- pandas

## 备注
- 分析算法可在 `core/analyzer.py` 中自定义和优化。
- API接口文档见：https://doc.steamdt.com/6279815m0
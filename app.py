import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# 1. 基础配置
st.set_page_config(page_title="柬埔寨工程机械行业诚信互助平台", layout="wide")
DB_FILE = "blacklist_v2.csv"
UPLOAD_DIR = "evidence_photos"

# 确保图片存储目录存在
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 2. 初始化数据库文件
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["ID", "登记时间", "单位名称/个人", "违约类型", "事实描述", "证据路径"])
    df.to_csv(DB_FILE, index=False)

# 3. 法律合规声明
def show_disclaimer():
    st.error("""
    **⚖️ 法律声明与使用须知（必读）**：
    1. 本平台为柬埔寨工程机械行业内部交流，旨在建立诚信环境。
    2. **提交即代表承诺**：您必须对所发内容的真实性负责。严禁恶意造谣、诽谤或发布虚假信息。
    3. 平台仅作为信息记录工具，不代表对任何单位的法律定性。
    4. 若发现恶意举报，平台保留删除权并可能追究相关责任。
    """)

# 4. 页面头部
st.title("🏗️ LIFT 工程机械行业诚信登记平台")
st.info("本页面信息由群友自发提供，提交后将立即在下方公示。")
show_disclaimer()

# --- 侧边栏：登记入口 ---
with st.sidebar:
    st.header("🖊️ 匿名登记举报")
    with st.form("blacklist_form", clear_on_submit=True):
        target = st.text_input("被登记对象 (公司名或个人姓名)", placeholder="必填")
        v_type = st.selectbox("违约类型", ["拖欠租金", "恶意损坏设备", "中介不结账", "违约鸽子", "安全隐患操作", "其他"])
        desc = st.text_area("详细经过描述", placeholder="请客观说明时间、地点、金额等事实")
        
        # 照片上传
        uploaded_file = st.file_uploader("上传证据照片 (合同/欠条/现场)", type=['png', 'jpg', 'jpeg'])
        
        agreement = st.checkbox("我承诺以上信息属实，并愿承担相关法律后果")
        submit = st.form_submit_button("🚀 立即发布公示")

        if submit:
            if not target or not agreement:
                st.error("请填写必填项并勾选承诺声明。")
            else:
                # 保存图片
                photo_path = "无照片"
                if uploaded_file is not None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    photo_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{uploaded_file.name}")
                    with open(photo_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # 写入数据（直接进入库文件）
                new_id = datetime.now().strftime("%Y%m%d%H%M%S")
                new_entry = {
                    "ID": new_id,
                    "登记时间": datetime.now().strftime("%Y-%m-%d"),
                    "单位名称/个人": target,
                    "违约类型": v_type,
                    "事实描述": desc,
                    "证据路径": photo_path
                }
                pd.DataFrame([new_entry]).to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success("发布成功！信息已在右侧列表中显示。")

# --- 主界面：公示与查询 ---
st.subheader("🔍 实时公示查询")
search = st.text_input("输入关键词搜索（如公司名）")

# 读取最新数据
try:
    df = pd.read_csv(DB_FILE)
    # 按时间倒序排列，让最新的在最上面
    df = df.iloc[::-1]
    
    if search:
        df = df[df['单位名称/个人'].str.contains(search, na=False)]

    if not df.empty:
        for index, row in df.iterrows():
            with st.expander(f"🚩 {row['单位名称/个人']} - {row['违约类型']} ({row['登记时间']})"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**事实详情**: {row['事实描述']}")
                with col2:
                    if row['证据路径'] != "无照片" and os.path.exists(row['证据路径']):
                        img = Image.open(row['证据路径'])
                        st.image(img, caption="点击可放大查看证据", use_container_width=True)
                    else:
                        st.caption("未上传照片证明")
    else:
        st.write("目前暂无登记记录。")
except Exception as e:
    st.write("数据加载中或暂无数据...")

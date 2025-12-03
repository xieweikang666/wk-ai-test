"""
Streamlit前端应用 - 网络探测数据AI分析
基于Streamlit的Python前端实现
"""
import streamlit as st
import requests
import pandas as pd
import time
from typing import Optional, Dict, Any
import json
import os

# 页面配置
st.set_page_config(
    page_title="网络探测数据AI分析",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="expanded"
)

# API配置
API_BASE_URL = "http://localhost:8000"

def call_chat_api(message: str) -> Dict[str, Any]:
    """
    调用聊天API
    
    Args:
        message: 用户消息
        
    Returns:
        API响应结果
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": message},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "无法连接到后端服务，请确保app.py正在运行"}
    except requests.exceptions.Timeout:
        return {"error": "请求超时，请稍后重试"}
    except Exception as e:
        return {"error": f"请求失败: {str(e)}"}

def check_api_health() -> bool:
    """
    检查API健康状态
    
    Returns:
        API是否可用
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def display_message(role: str, content: str, chart_url: Optional[str] = None, sql: Optional[str] = None):
    """
    显示消息
    
    Args:
        role: 消息角色 (user/assistant)
        content: 消息内容
        chart_url: 图表URL
        sql: SQL查询语句
    """
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            # 显示分析结果
            st.write(content)
            
            # 显示SQL查询
            if sql:
                with st.expander("查看SQL查询", expanded=False):
                    st.code(sql, language="sql")
            
            # 显示图表
            if chart_url:
                try:
                    st.image(f"{API_BASE_URL}{chart_url}", caption="分析图表", use_column_width=True)
                except Exception as e:
                    st.error(f"图表加载失败: {e}")

def main():
    """主函数"""
    # 页面标题
    st.title("🌐 网络探测数据AI分析")
    st.markdown("---")
    
    # 侧边栏配置
    with st.sidebar:
        st.header("🔧 系统状态")
        
        # 检查API连接
        if check_api_health():
            st.success("✅ 后端服务连接正常")
        else:
            st.error("❌ 后端服务连接失败")
            st.info("请先启动后端服务：`python3 app.py`")
        
        st.markdown("---")
        st.header("📋 快速示例")
        
        # 示例问题
        examples = [
            "统计近1h各运营商的探测设备数量",
            "分析各个目标节点的丢包情况", 
            "查看浙江电信的网络覆盖质量",
            "对比不同运营商的网络性能",
            "查询过去24小时各省份的平均延迟",
            "绘制辽宁到上海的RTT分布图"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}"):
                st.session_state.selected_example = example
    
    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示欢迎信息
    if not st.session_state.messages:
        st.markdown("""
        ## 👋 你好！我是网络探测数据分析助手
        
        我可以帮你分析网络探测数据，包括：
        
        📊 **设备性能分析** - 探测设备的运行状态和性能指标
        🎯 **节点丢包统计** - 各目标节点的网络连通性分析  
        🗺️ **地区覆盖情况** - 不同省份的网络覆盖质量
        📡 **运营商分布** - 三大运营商的网络性能对比
        
        💡 **使用提示**：可以直接输入问题，或点击左侧的示例问题
        """)
    
    # 处理示例问题
    if "selected_example" in st.session_state:
        example = st.session_state.selected_example
        del st.session_state.selected_example
        
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": example})
        
        # 显示用户消息
        display_message("user", example)
        
        # 调用API
        with st.spinner("🤔 AI正在分析数据..."):
            response = call_chat_api(example)
        
        if "error" in response:
            st.error(response["error"])
        else:
            # 显示AI回复
            display_message(
                "assistant", 
                response.get("answer", ""),
                response.get("chart_url"),
                response.get("sql")
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.get("answer", ""),
                "chart_url": response.get("chart_url"),
                "sql": response.get("sql")
            })
    
    # 显示历史消息
    for message in st.session_state.messages:
        if message["role"] == "user":
            display_message("user", message["content"])
        else:
            display_message(
                "assistant",
                message["content"],
                message.get("chart_url"),
                message.get("sql")
            )
    
    # 用户输入
    st.markdown("---")
    
    # 输入区域
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "💬 输入你的问题：",
            placeholder="例如：统计近1h各运营商的探测设备数量",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("📤 发送", type="primary")
    
    # 处理用户输入
    if send_button and user_input.strip():
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 显示用户消息
        display_message("user", user_input)
        
        # 调用API
        with st.spinner("🤔 AI正在分析数据..."):
            response = call_chat_api(user_input)
        
        if "error" in response:
            st.error(response["error"])
        else:
            # 显示AI回复
            display_message(
                "assistant",
                response.get("answer", ""),
                response.get("chart_url"),
                response.get("sql")
            )
            
            # 保存到历史
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.get("answer", ""),
                "chart_url": response.get("chart_url"),
                "sql": response.get("sql")
            })
        
        # 刷新页面以清空输入框
        st.rerun()
    
    # 底部信息
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📁 数据源：ClickHouse detect_ping_log")
    
    with col2:
        st.info("🤖 AI模型：GPT-4o mini")
    
    with col3:
        st.info("🔍 查询限制：最多100万行")

if __name__ == "__main__":
    main()
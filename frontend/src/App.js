import React, { useState, useEffect } from 'react';
import { Layout, message, Spin } from 'antd';
import ChatInterface from './components/ChatInterface';
import './App.css';

const { Header, Content } = Layout;

function App() {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 测试后端连接
    const testBackend = async () => {
      try {
        const response = await fetch('/health');
        if (response.ok) {
          console.log('后端连接正常');
        } else {
          message.warning('后端服务连接异常，请检查后端是否启动');
        }
      } catch (error) {
        message.warning('无法连接到后端服务，请确保后端在localhost:8000运行');
      }
    };

    testBackend();
  }, []);

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="header-content">
          <span className="header-title">🌐 网络探测数据AI分析平台</span>
        </div>
      </Header>
      <Content className="app-content">
        <ChatInterface loading={loading} setLoading={setLoading} />
      </Content>
    </Layout>
  );
}

export default App;
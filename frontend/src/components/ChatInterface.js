import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  message, 
  Spin, 
  Typography, 
  Space, 
  Tag, 
  Divider,
  Alert,
  Tooltip,
  Row,
  Col
} from 'antd';
import { 
  SendOutlined, 
  RobotOutlined, 
  UserOutlined, 
  CodeOutlined,
  BarChartOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import DataTable from './DataTable';
import ChartDisplay from './ChartDisplay';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

const ChatInterface = ({ loading, setLoading }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 预设的查询建议
  const suggestions = [
    "统计近1h各运营商的探测设备数量",
    "分析各个目标节点的丢包情况", 
    "查看浙江电信的网络覆盖质量",
    "对比不同运营商的网络性能",
    "分析昨天晚高峰19-23点各目标节点覆盖区域的质量"
  ];

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
    setLoading(true);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputValue.trim() })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.answer,
        sql: data.sql,
        chartUrl: data.chart_url,
        qualitySummary: data.quality_summary,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      message.error('分析过程中出现错误：' + error.message);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: `抱歉，分析过程中出现了错误：${error.message}`,
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const MessageItem = ({ message }) => {
    if (message.type === 'user') {
      return (
        <Row justify="end" style={{ marginBottom: 16 }}>
          <Col xs={20} sm={16} md={12} lg={10}>
            <Card 
              size="small"
              style={{ 
                backgroundColor: '#1890ff', 
                color: 'white',
                borderRadius: 12,
                marginLeft: 'auto'
              }}
              bodyStyle={{ padding: '12px 16px' }}
            >
              <Space direction="vertical" size={4}>
                <Space>
                  <UserOutlined />
                  <Text style={{ color: 'white', fontWeight: 500 }}>你</Text>
                </Space>
                <Text style={{ color: 'white' }}>{message.content}</Text>
              </Space>
            </Card>
          </Col>
        </Row>
      );
    }

    return (
      <Row justify="start" style={{ marginBottom: 16 }}>
        <Col xs={20} sm={16} md={14} lg={12}>
          <Card 
            size="small"
            style={{ 
              backgroundColor: 'white',
              borderRadius: 12,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
            bodyStyle={{ padding: '16px' }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Space>
                <RobotOutlined style={{ color: '#52c41a' }} />
                <Text strong>AI分析助手</Text>
                {message.qualitySummary && (
                  <Tooltip title="查询质量评分">
                    <Tag color="green" icon={<InfoCircleOutlined />}>
                      {message.qualitySummary}
                    </Tag>
                  </Tooltip>
                )}
              </Space>

              {/* SQL代码块 */}
              {message.sql && (
                <>
                  <Space>
                    <CodeOutlined style={{ color: '#1890ff' }} />
                    <Text strong style={{ color: '#1890ff' }}>生成的查询SQL</Text>
                  </Space>
                  <div className="sql-code">
                    <SyntaxHighlighter 
                      language="sql" 
                      style={tomorrow}
                      customStyle={{
                        background: 'transparent',
                        padding: 0,
                        margin: 0,
                        fontSize: '12px'
                      }}
                    >
                      {message.sql}
                    </SyntaxHighlighter>
                  </div>
                  <Divider style={{ margin: '12px 0' }} />
                </>
              )}

              {/* 分析内容 */}
              <div className="markdown-content">
                <ReactMarkdown
                  components={{
                    h1: ({children}) => <Title level={2}>{children}</Title>,
                    h2: ({children}) => <Title level={3}>{children}</Title>,
                    h3: ({children}) => <Title level={4}>{children}</Title>,
                    table: ({children}) => <DataTable data={children} />,
                    code: ({node, inline, className, children, ...props}) => {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={tomorrow}
                          language={match[1]}
                          PreTag="div"
                          customStyle={{
                            borderRadius: 6,
                            margin: '8px 0'
                          }}
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    }
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>

              {/* 图表展示 */}
              {message.chartUrl && (
                <ChartDisplay chartUrl={message.chartUrl} />
              )}

              {message.isError && (
                <Alert
                  message="错误"
                  description={message.content}
                  type="error"
                  showIcon
                />
              )}
            </Space>
          </Card>
        </Col>
      </Row>
    );
  };

  return (
    <Card
      title="💬 智能分析对话"
      style={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column' 
      }}
      bodyStyle={{ 
        height: 'calc(100% - 57px)', 
        padding: 0, 
        display: 'flex', 
        flexDirection: 'column' 
      }}
    >
      {/* 消息列表 */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        padding: '16px 24px',
        backgroundColor: '#fafafa'
      }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <Title level={3} color="textSecondary">
              你好！我是网络探测数据分析助手
            </Title>
            <Paragraph color="textSecondary">
              我可以帮你分析网络探测数据，包括：设备性能分析、节点丢包统计、地区覆盖情况、运营商分布等
            </Paragraph>
            
            <div style={{ marginTop: 24 }}>
              <Title level={5}>常用查询：</Title>
              <Space wrap>
                {suggestions.map((suggestion, index) => (
                  <Tag 
                    key={index}
                    style={{ 
                      cursor: 'pointer', 
                      marginBottom: 8,
                      padding: '4px 12px'
                    }}
                    onClick={() => setInputValue(suggestion)}
                  >
                    {suggestion}
                  </Tag>
                ))}
              </Space>
            </div>
          </div>
        ) : (
          messages.map(message => (
            <MessageItem key={message.id} message={message} />
          ))
        )}
        
        {isTyping && (
          <Row justify="start" style={{ marginBottom: 16 }}>
            <Col xs={20} sm={16} md={14} lg={12}>
              <Card size="small" style={{ borderRadius: 12 }}>
                <Space>
                  <Spin size="small" />
                  <Text type="secondary">AI正在分析数据...</Text>
                </Space>
              </Card>
            </Col>
          </Row>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div style={{ 
        padding: '16px 24px', 
        borderTop: '1px solid #f0f0f0',
        backgroundColor: 'white'
      }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入你的问题，例如：统计近1h各运营商的探测设备数量"
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={isTyping}
            style={{ resize: 'none' }}
          />
          <Button 
            type="primary" 
            icon={<SendOutlined />}
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            loading={isTyping}
            style={{ height: 'auto' }}
          >
            发送
          </Button>
        </Space.Compact>
      </div>
    </Card>
  );
};

export default ChatInterface;
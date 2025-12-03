import React, { useState } from 'react';
import { Card, Image, Button, Space, Modal, Typography } from 'antd';
import { 
  EyeOutlined, 
  DownloadOutlined, 
  ExpandOutlined,
  PictureOutlined 
} from '@ant-design/icons';

const { Text } = Typography;

const ChartDisplay = ({ chartUrl }) => {
  const [previewVisible, setPreviewVisible] = useState(false);

  const handlePreview = () => {
    setPreviewVisible(true);
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = chartUrl;
    link.download = `network-analysis-chart-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!chartUrl) {
    return null;
  }

  return (
    <div style={{ margin: '16px 0' }}>
      <Card
        size="small"
        title={
          <Space>
            <PictureOutlined style={{ color: '#52c41a' }} />
            <Text strong>数据图表</Text>
          </Space>
        }
        extra={
          <Space>
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={handlePreview}
              title="预览图表"
            />
            <Button
              type="text"
              size="small"
              icon={<DownloadOutlined />}
              onClick={handleDownload}
              title="下载图表"
            />
          </Space>
        }
        style={{
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}
        bodyStyle={{ padding: 16 }}
      >
        <div style={{ textAlign: 'center' }}>
          <Image
            src={chartUrl}
            alt="分析图表"
            style={{
              maxWidth: '100%',
              height: 'auto',
              borderRadius: 6,
              border: '1px solid #f0f0f0'
            }}
            preview={false}
            onError={(e) => {
              console.error('图表加载失败:', e);
              e.target.style.display = 'none';
            }}
          />
        </div>
      </Card>

      <Modal
        title="图表预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="download" icon={<DownloadOutlined />} onClick={handleDownload}>
            下载图表
          </Button>,
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>
        ]}
        width="90%"
        style={{ top: 20 }}
        bodyStyle={{ padding: 0, textAlign: 'center' }}
      >
        <Image
          src={chartUrl}
          alt="分析图表预览"
          style={{
            maxWidth: '100%',
            maxHeight: '70vh',
            objectFit: 'contain'
          }}
          preview={false}
        />
      </Modal>
    </div>
  );
};

export default ChartDisplay;
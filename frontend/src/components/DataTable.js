import React from 'react';
import { Table, Typography } from 'antd';
import { BarChartOutlined } from '@ant-design/icons';

const { Text } = Typography;

const DataTable = ({ children }) => {
  // 将ReactMarkdown的table children转换为Ant Design Table的数据格式
  const parseTableData = (tableElement) => {
    if (!tableElement || !tableElement.props) {
      return { columns: [], dataSource: [] };
    }

    const rows = tableElement.props.children || [];
    if (!Array.isArray(rows)) {
      return { columns: [], dataSource: [] };
    }

    let headers = [];
    let dataRows = [];

    rows.forEach((row, index) => {
      if (!row || !row.props) return;
      
      const cells = row.props.children || [];
      if (!Array.isArray(cells)) return;

      const cellData = cells.map(cell => 
        cell && cell.props ? (cell.props.children || '') : ''
      ).filter(text => text !== '');

      if (cellData.length === 0) return;

      // 第一行作为表头
      if (index === 0) {
        headers = cellData.map((header, i) => ({
          title: header,
          dataIndex: `col_${i}`,
          key: `col_${i}`,
          ellipsis: true,
          render: (text) => {
            // 尝试识别数值类型并右对齐
            const isNumeric = !isNaN(text) && text !== '';
            return (
              <div style={{ textAlign: isNumeric ? 'right' : 'left', width: '100%' }}>
                <Text 
                  code={isNumeric}
                  style={{ 
                    fontSize: '12px',
                    fontFamily: isNumeric ? 'Monaco, Menlo, monospace' : 'inherit'
                  }}
                >
                  {text}
                </Text>
              </div>
            );
          }
        }));
      } else {
        // 数据行
        const rowData = {};
        cellData.forEach((cell, i) => {
          rowData[`col_${i}`] = cell;
        });
        rowData.key = index;
        dataRows.push(rowData);
      }
    });

    return { columns: headers, dataSource: dataRows };
  };

  const { columns, dataSource } = parseTableData(children);

  if (!columns.length || !dataSource.length) {
    return <div>暂无表格数据</div>;
  }

  return (
    <div style={{ margin: '16px 0' }}>
      <div style={{ marginBottom: 8 }}>
        <BarChartOutlined style={{ marginRight: 8, color: '#1890ff' }} />
        <Text strong style={{ color: '#1890ff' }}>数据表格</Text>
      </div>
      <Table
        columns={columns}
        dataSource={dataSource}
        pagination={false}
        size="small"
        scroll={{ x: 'max-content' }}
        bordered
        style={{
          backgroundColor: 'white',
          borderRadius: 6,
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}
        rowClassName={(record, index) => 
          index % 2 === 0 ? 'table-row-light' : 'table-row-dark'
        }
      />
    </div>
  );
};

export default DataTable;
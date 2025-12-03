# detect_ping_log 数据表结构文档

## 表基本信息

- **数据库**: detect
- **表名**: detect_ping_log
- **引擎**: ClickHouse MergeTree

## 字段说明

### 时间字段
- **timestamp** (Int64): 时间戳，单位：秒（Unix timestamp）
  - 用于时间范围查询和排序
  - 建议使用时间范围过滤以提高查询性能

### 任务相关
- **task_name** (String): 探测任务名称
  - 常见值：edge_l1_detect, edge_l2_detect 等
  - 适合作为过滤条件

### 源端信息
- **src_isp** (String): 源运营商
  - 常见值：chinatelecom（电信）、chinamobile（移动）、chinaunicom（联通）
  - 适合做 GROUP BY 和过滤
- **src_province** (String): 源省份
  - 省份拼音小写，如：liaoning（辽宁）、beijing（北京）、shanghai（上海）
  - 适合做 GROUP BY 和过滤
- **src_node** (String): 源节点标识
- **hostname** (String): 源主机名

### 目标端信息
- **target_node** (String): 目标节点标识
  - 适合做过滤和 GROUP BY
- **target_hostname** (String): 目标主机名

### 性能指标
- **avg_rtt** (Float64): 平均 RTT（Round Trip Time），单位：毫秒
  - 核心指标，用于分析网络延迟
  - 适合做聚合计算：AVG, MAX, MIN, P95, P99
- **avg_lost** (Float64): 平均丢包率，范围 0-1
  - 核心指标，用于分析网络质量
  - 适合做聚合计算：AVG, MAX, MIN
- **packet_loss** (Int64): 丢包数量
- **packet_total** (Int64): 总包数量

## 查询最佳实践

### 1. 时间范围查询（必须）
```sql
-- 推荐：使用时间戳范围
WHERE timestamp >= 1609459200 AND timestamp <= 1609545600

-- 避免：全表扫描
WHERE toDate(timestamp) = '2024-01-01'
```

### 2. 常用聚合维度
- 按省份聚合：`GROUP BY src_province`
- 按运营商聚合：`GROUP BY src_isp`
- 按任务聚合：`GROUP BY task_name`
- 按目标节点聚合：`GROUP BY target_node`
- 组合聚合：`GROUP BY src_province, src_isp, task_name`

### 3. 常用指标计算
```sql
-- 平均 RTT
AVG(avg_rtt) as avg_rtt

-- 最大 RTT
MAX(avg_rtt) as max_rtt

-- 丢包率
AVG(avg_lost) as avg_loss_rate

-- 样本数量
COUNT(*) as sample_count
```

### 4. 性能优化建议
- **必须包含时间范围过滤**：避免全表扫描
- **使用 LIMIT**：限制返回行数，建议不超过 100 万行
- **优先使用索引字段**：timestamp, task_name, src_isp, src_province
- **避免 SELECT ***：只选择需要的字段

### 5. 典型查询模式

#### 查询某时间段内各省份的平均 RTT
```sql
SELECT 
    src_province,
    AVG(avg_rtt) as avg_rtt,
    COUNT(*) as count
FROM detect.detect_ping_log
WHERE timestamp >= 1609459200 AND timestamp <= 1609545600
GROUP BY src_province
ORDER BY avg_rtt DESC
LIMIT 1000000
```

#### 查询某运营商在特定省份的丢包率趋势
```sql
SELECT 
    toStartOfHour(toDateTime(timestamp)) as hour,
    AVG(avg_lost) as avg_loss_rate,
    COUNT(*) as count
FROM detect.detect_ping_log
WHERE timestamp >= 1609459200 
  AND timestamp <= 1609545600
  AND src_isp = 'chinatelecom'
  AND src_province = 'liaoning'
GROUP BY hour
ORDER BY hour
LIMIT 1000000
```

#### 查询某任务到特定目标节点的 RTT 分布
```sql
SELECT 
    target_node,
    AVG(avg_rtt) as avg_rtt,
    quantile(0.95)(avg_rtt) as p95_rtt,
    MAX(avg_rtt) as max_rtt,
    COUNT(*) as count
FROM detect.detect_ping_log
WHERE timestamp >= 1609459200 
  AND timestamp <= 1609545600
  AND task_name = 'edge_l1_detect'
GROUP BY target_node
ORDER BY avg_rtt DESC
LIMIT 1000000
```

## 索引情况

- **主键**: (timestamp, task_name)
- **排序键**: (timestamp, task_name, src_isp, src_province)
- **分区**: 通常按日期分区（具体需确认）

## 注意事项

1. **时间戳格式**: timestamp 字段是 Int64 类型，存储的是 Unix 时间戳（秒）
2. **字段大小写**: 所有字段名都是小写
3. **空值处理**: 某些字段可能为空，查询时注意 NULL 处理
4. **数据量**: 表数据量可能很大，务必使用时间范围过滤
5. **查询限制**: 单次查询建议不超过 100 万行，避免内存溢出



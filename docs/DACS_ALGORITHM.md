# Dependency-Aware CRUD Sequence (DACS) 算法文档

## 1. 算法概述

**DACS (Dependency-Aware CRUD Sequence)** 是一种基于操作依赖图（Operation Dependency Graph, ODG）的RESTful API测试序列生成算法。该算法通过分析API操作之间的资源依赖关系，生成符合CRUD语义的测试序列，用于差分测试（Differential Testing）场景。

## 2. 核心设计理念

### 2.1 依赖感知（Dependency-Aware）
- 通过ODG分析API操作之间的依赖关系
- 自动追溯前置依赖链，确保资源创建顺序正确
- 例如：`PUT /projects/{id}/badges/{badge_id}` 依赖于 `POST /projects` 和 `POST /projects/{id}/badges`

### 2.2 CRUD语义排序
按照资源生命周期的自然顺序组织操作：
```
POST (创建) → GET (读取) → PUT/PATCH (更新) → DELETE (删除)
```

## 3. 算法配置参数

| 参数 | 最小值 | 最大值 | 说明 |
|------|--------|--------|------|
| `SEQUENCE_LENGTH` | 5 | 25 | 生成序列的总长度范围 |
| `PREREQUISITE_CHAIN` | 1 | 8 | 前置依赖链的长度范围 |
| `DELETE_COUNT` | 1 | 3 | DELETE操作的数量范围 |

## 4. DELETE策略

算法支持三种DELETE操作添加策略，运行时随机选择以增加测试多样性：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `CORRESPONDING_ONLY` | 只添加序列中POST操作对应的DELETE | 严格模式，验证资源完整生命周期 |
| `RANDOM_ONLY` | 随机添加DELETE操作 | 探索模式，发现边界情况 |
| `MIXED` | 混合模式：一半对应+一半随机 | 平衡模式，兼顾覆盖率和探索性 |

## 5. 算法流程（五阶段）

### 阶段一：起始节点选择
```
60% 概率 → 选择有出度的POST节点（生成更长的有意义序列）
40% 概率 → 随机选择POST节点（确保独立操作也能被测试）
```

### 阶段二：前置依赖追溯
- 使用完整拓扑排序追溯所有POST依赖链
- 递归处理多层级依赖
- 动态限制链长度（1-8），但确保关键依赖不被截断

### 阶段三：后续操作收集
- 收集依赖前置链的所有操作
- 按CRUD语义排序：POST → GET → PUT/PATCH
- 同类型操作按出度排序（出度大的优先）

### 阶段四：GET操作强制添加
- 检查序列是否包含GET操作
- 优先添加与POST操作相关的GET操作
- 将GET操作插入到相关POST之后的合适位置

### 阶段五：CRUD顺序验证与DELETE添加
- 重新检查并调整序列，确保POST在PUT之前
- 根据当前策略添加DELETE操作
- DELETE操作添加到序列末尾（LIFO原则：后创建的先删除）

## 6. POST-DELETE映射规则

算法通过智能端点匹配建立POST和DELETE操作的对应关系：

### 匹配场景

| 场景 | POST端点 | DELETE端点 | 匹配分数 |
|------|----------|------------|----------|
| 标准模式 | `/resources` | `/resources/{id}` | 100 |
| 嵌套资源 | `/parent/{parentId}/resources` | `/parent/{parentId}/resources/{id}` | 100 |
| 后缀模式 | `/resources` | `/resources/{id}` | 90 |
| 完全相同 | `/resources` | `/resources` | 50 |

### 匹配算法核心逻辑
```java
// DELETE端点 = POST端点 + /{pathParameter}
// 例如：DELETE /resources/{id} 匹配 POST /resources
```

## 7. 示例序列

### 输入：目标操作
```
PUT /projects/{id}/badges/{badge_id}
```

### 生成的DACS序列
```
1. POST /projects                          # 创建项目（根资源）
2. POST /projects/{id}/badges              # 创建徽章（子资源）
3. GET /projects/{id}                      # 读取项目
4. GET /projects/{id}/badges/{badge_id}    # 读取徽章
5. PUT /projects/{id}/badges/{badge_id}    # 更新徽章（目标操作）
6. DELETE /projects/{id}/badges/{badge_id} # 删除徽章
7. DELETE /projects/{id}                   # 删除项目
```

## 8. 关键特性

### 8.1 完整依赖追溯
- 确保所有前置POST操作都被执行
- 避免因资源不存在导致的404错误

### 8.2 CRUD语义保证
- POST必定在对应的PUT/PATCH之前
- GET操作确保存在于序列中
- DELETE操作按LIFO原则添加

### 8.3 多样性设计
- 动态序列长度（5-25）
- 随机DELETE策略
- 随机前置链长度限制
- 60/40概率的起始节点选择策略

## 9. 类图

```
┌─────────────────────────────────────────────────────────────┐
│                   DiffBasedGraphSorter                       │
├─────────────────────────────────────────────────────────────┤
│ - graph: OperationDependencyGraph                           │
│ - postToDeleteMap: Map<Operation, Operation>                │
│ - postNodes: List<OperationNode>                            │
│ - deleteNodes: List<OperationNode>                          │
│ - getNodes: List<OperationNode>                             │
│ - currentDeleteStrategy: DeleteStrategy                      │
│ - currentMaxDepth: int                                       │
├─────────────────────────────────────────────────────────────┤
│ + getTestSequence(): void                                    │
│ + computePostToDeleteMap(): void                             │
│ - findCompletePrerequisiteChain(): List<OperationNode>      │
│ - reorderSequenceForCrudSemantics(): void                   │
│ - addCorrespondingDeletes(): void                           │
│ - addRandomDeletes(): void                                   │
│ - getCrudOrder(HttpMethod): int                             │
└─────────────────────────────────────────────────────────────┘
```

## 10. 学术命名建议

| 名称 | 英文全称 | 特点描述 |
|------|----------|----------|
| **DACS** | Dependency-Aware CRUD Sequence | 推荐，强调依赖感知+CRUD语义 |
| TGOS | Topology-Guided Operation Sequence | 强调拓扑排序特性 |
| RLTS | Resource Lifecycle Test Sequence | 强调资源生命周期 |
| DDTS | Dependency-Driven Test Sequence | 简洁明了 |
| CODS | CRUD-Ordered Dependency Sequence | 强调CRUD排序 |
| PCTS | Prerequisite-Chained Test Sequence | 强调前置依赖链追溯 |

## 11. 适用场景

1. **差分测试（Differential Testing）**：对比API响应与数据库状态
2. **API回归测试**：验证资源CRUD操作的完整性
3. **依赖关系验证**：检测API操作间的隐式依赖
4. **边界条件探索**：通过随机策略发现边界情况

## 12. 参考文献

- RESTful API设计规范
- OpenAPI Specification
- 操作依赖图（Operation Dependency Graph）理论

---

*文档生成时间：2026-01-17*  
*项目：RestSqlDiff - RESTful API与本地MySQL模型差分测试工具*


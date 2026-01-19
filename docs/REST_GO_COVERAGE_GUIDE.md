# REST-Go 本地部署与代码覆盖率测试指南

## 1. 概述

REST-Go 是一套用于 REST API 测试的 Go 语言基准套件。由于官方仓库可能已迁移，以下提供多种获取方式和替代方案。

---

## 2. 获取 REST-Go

### 方式1：从 EvoMaster Benchmark 获取
```bash
git clone https://github.com/EMResearch/EMB.git
cd EMB
# REST-Go 服务位于 go 目录下
```

### 方式2：使用类似的 Go REST API 项目
推荐使用以下替代项目：

| 项目 | 描述 | GitHub |
|------|------|--------|
| go-restful-api | 简单的 Go REST API | https://github.com/qiangxue/go-rest-api |
| gin-gonic/gin | 流行的 Go Web 框架 | https://github.com/gin-gonic/gin |
| go-swagger | Swagger 生成的 Go API | https://github.com/go-swagger/go-swagger |

---

## 3. Go 语言代码覆盖率测试方法

### 3.1 安装 Go 环境
```bash
# Windows - 使用 Chocolatey
choco install golang

# 或从官网下载
# https://golang.org/dl/
```

### 3.2 验证安装
```powershell
go version
# 应显示: go version go1.21.x windows/amd64
```

---

## 4. 使用 Go 内置覆盖率工具

### 4.1 基本覆盖率测试
```bash
# 运行测试并生成覆盖率报告
go test -coverprofile=coverage.out ./...

# 查看覆盖率百分比
go tool cover -func=coverage.out

# 生成 HTML 报告
go tool cover -html=coverage.out -o coverage.html
```

### 4.2 带覆盖率的服务运行 (Go 1.20+)

从 Go 1.20 开始，支持在运行时收集覆盖率：

```bash
# 1. 编译带覆盖率的二进制文件
go build -cover -o myapi-cover.exe ./cmd/api

# 2. 设置覆盖率输出目录
$env:GOCOVERDIR="./coverage_data"
mkdir coverage_data

# 3. 运行服务
./myapi-cover.exe

# 4. 发送测试请求后，停止服务 (Ctrl+C)

# 5. 合并覆盖率数据
go tool covdata percent -i=./coverage_data

# 6. 转换为传统格式
go tool covdata textfmt -i=./coverage_data -o=coverage.out

# 7. 生成 HTML 报告
go tool cover -html=coverage.out -o coverage.html
```

---

## 5. 示例：测试一个简单的 Go REST API

### 5.1 创建示例项目
```bash
mkdir rest-api-demo
cd rest-api-demo
go mod init rest-api-demo
```

### 5.2 创建 main.go
```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type Item struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

var items = []Item{
    {ID: 1, Name: "Item 1"},
    {ID: 2, Name: "Item 2"},
}

func getItems(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(items)
}

func createItem(w http.ResponseWriter, r *http.Request) {
    var item Item
    json.NewDecoder(r.Body).Decode(&item)
    item.ID = len(items) + 1
    items = append(items, item)
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(item)
}

func main() {
    http.HandleFunc("/items", func(w http.ResponseWriter, r *http.Request) {
        switch r.Method {
        case "GET":
            getItems(w, r)
        case "POST":
            createItem(w, r)
        default:
            http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        }
    })
    
    log.Println("Server starting on :8080...")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### 5.3 运行覆盖率测试
```powershell
# 1. 编译带覆盖率的版本
go build -cover -o api-cover.exe .

# 2. 创建覆盖率目录
mkdir coverage_data

# 3. 设置环境变量并运行
$env:GOCOVERDIR="./coverage_data"
Start-Process -FilePath "./api-cover.exe"

# 4. 发送测试请求
Invoke-RestMethod -Uri "http://localhost:8080/items" -Method GET
Invoke-RestMethod -Uri "http://localhost:8080/items" -Method POST -Body '{"name":"New Item"}' -ContentType "application/json"

# 5. 停止服务 (在另一个终端)
Stop-Process -Name "api-cover"

# 6. 查看覆盖率
go tool covdata percent -i=./coverage_data
```

---

## 6. 与 RestSqlDiff 集成

### 6.1 配置 Go API
在 `apis/` 目录下创建新的 API 配置：

```yaml
# apis/go-demo/api-config.yml
api:
  name: "go-demo"
  base_url: "http://localhost:8080"
  specification: "specifications/openapi.json"

authentication:
  type: none
```

### 6.2 创建 OpenAPI 规范
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Go Demo API",
    "version": "1.0.0"
  },
  "servers": [
    {"url": "http://localhost:8080"}
  ],
  "paths": {
    "/items": {
      "get": {
        "operationId": "getItems",
        "responses": {
          "200": {
            "description": "List of items"
          }
        }
      },
      "post": {
        "operationId": "createItem",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "name": {"type": "string"}
                }
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Item created"
          }
        }
      }
    }
  }
}
```

### 6.3 运行测试流程
```powershell
# 1. 启动带覆盖率的 Go API
$env:GOCOVERDIR="./coverage_data"
Start-Process -FilePath "./api-cover.exe"

# 2. 运行 RestSqlDiff 测试
./gradlew run

# 3. 停止 API 服务
Stop-Process -Name "api-cover"

# 4. 收集覆盖率数据
go tool covdata textfmt -i=./coverage_data -o=coverage.out
go tool cover -html=coverage.out -o coverage_report.html
```

---

## 7. 实时覆盖率监控脚本

创建 PowerShell 脚本自动化整个流程：

```powershell
# coverage_test.ps1

param(
    [string]$ApiPath = ".",
    [string]$Duration = 300  # 测试时长（秒）
)

# 1. 编译
Write-Host "Building with coverage..."
Set-Location $ApiPath
go build -cover -o api-cover.exe .

# 2. 准备目录
$coverDir = "./coverage_data_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $coverDir -Force

# 3. 启动服务
$env:GOCOVERDIR = $coverDir
$process = Start-Process -FilePath "./api-cover.exe" -PassThru

Write-Host "API started (PID: $($process.Id))"
Write-Host "Running tests for $Duration seconds..."

# 4. 等待测试完成
Start-Sleep -Seconds $Duration

# 5. 停止服务
Stop-Process -Id $process.Id -Force
Write-Host "API stopped"

# 6. 生成报告
Write-Host "Generating coverage report..."
go tool covdata percent -i=$coverDir
go tool covdata textfmt -i=$coverDir -o=coverage.out
go tool cover -html=coverage.out -o=coverage_report.html

Write-Host "Coverage report generated: coverage_report.html"
```

---

## 8. 其他 Go REST API 基准选择

如果无法获取 REST-Go，可以考虑以下项目：

### 8.1 Gin-based API
```bash
git clone https://github.com/eddycjy/go-gin-example.git
cd go-gin-example
go build -cover -o gin-cover.exe .
```

### 8.2 Echo-based API
```bash
git clone https://github.com/labstack/echo.git
cd echo/cookbook/crud
go build -cover -o echo-cover.exe .
```

### 8.3 自定义 Petstore 实现
可以使用 go-swagger 生成 Petstore API：
```bash
go install github.com/go-swagger/go-swagger/cmd/swagger@latest
swagger generate server -f petstore.json -A petstore
```

---

## 9. 覆盖率数据可视化

### 9.1 使用 Python 绘图
```python
import matplotlib.pyplot as plt
import re

# 解析覆盖率文件
def parse_coverage(filename):
    coverage_data = {}
    with open(filename, 'r') as f:
        for line in f:
            match = re.match(r'(.+):(\d+\.\d+)%', line)
            if match:
                pkg, pct = match.groups()
                coverage_data[pkg] = float(pct)
    return coverage_data

# 绘制覆盖率图
data = parse_coverage('coverage_summary.txt')
plt.figure(figsize=(12, 6))
plt.bar(data.keys(), data.values())
plt.xlabel('Package')
plt.ylabel('Coverage %')
plt.title('Code Coverage by Package')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('coverage_by_package.png')
```

---

## 10. 常见问题

### Q1: Go 版本不支持 -cover 标志
**A:** 需要 Go 1.20 或更高版本。升级 Go：
```bash
choco upgrade golang
```

### Q2: 覆盖率数据为空
**A:** 确保：
1. `GOCOVERDIR` 环境变量正确设置
2. 程序正常终止（不是强制 kill -9）
3. 目录有写入权限

### Q3: 无法合并覆盖率数据
**A:** 使用 `go tool covdata merge` 合并多次运行的数据：
```bash
go tool covdata merge -i=./run1,./run2 -o=./merged
```

---

## 11. 参考资源

- [Go Coverage Profiling](https://go.dev/blog/cover)
- [Go 1.20 Coverage](https://go.dev/testing/coverage/)
- [EvoMaster](https://github.com/EMResearch/EvoMaster)
- [RESTler](https://github.com/microsoft/restler-fuzzer)


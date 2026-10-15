# REA (Reverse Engineer Anything) Antigravity 설치 및 연동 가이드

## 1. 개요
[REA (Reverse Engineer Anything)](https://github.com/morluto/rea)는 웹 애플리케이션, Electron/JavaScript 앱, .NET 어셈블리부터 네이티브 바이너리까지 소스 코드 없이도 AI 에이전트가 직접 분석하고 역공학을 수행할 수 있도록 지원하는 **MCP (Model Context Protocol) 기반 툴킷**입니다.

Antigravity는 REA의 공식 지원 클라이언트(`--client antigravity`) 목록에 포함되어 있으며, REA의 MCP 서버 및 전문 워크플로 스킬(Skill)을 등록하여 대화창에서 바로 리버스 엔지니어링을 지시할 수 있습니다.

---

## 2. 사전 필수 요구사항 (Prerequisites)

REA를 실행하려면 **Node.js (v22.19+ 이상 권장)** 가 필요합니다.
현재 Windows 시스템에 Node.js가 설치되어 있지 않다면 아래 명령어로 먼저 설치합니다.

### Node.js LTS 설치 (PowerShell 관리자 권한 권장)
```powershell
winget install OpenJS.NodeJS.LTS
```
> 설치 완료 후 터미널을 다시 열어 `node -v` 및 `npm -v`가 정상 출력되는지 확인합니다.

---

## 3. Antigravity 자동 설치 및 연동

터미널(PowerShell)에서 아래 명령어를 실행하여 Antigravity에 REA MCP 서버와 스킬을 자동으로 구성합니다.

```powershell
npx -y rea-agents@latest setup --client antigravity
```

### 상호작용 프롬프트 안내
1. 도구 및 스킬 등록 승인 여부를 묻는 프롬프트가 나타나면 내용을 확인하고 승인(`y` 또는 `Enter`)합니다.
2. 실행 시 Antigravity의 글로벌 설정 파일(`~/.gemini/config/mcp_config.json`)에 `rea` MCP 서버가 등록되고, 스킬 디렉토리에 전용 워크플로 지침이 설치됩니다.

---

## 4. 수동 연동 방법 (필요한 경우)

자동 설정을 사용하지 않고 수동으로 등록하려면 다음 파일들을 직접 수정하거나 생성할 수 있습니다.

### 4.1 MCP 서버 등록 (`~/.gemini/config/mcp_config.json`)
파일 위치: `C:\Users\<사용자명>\.gemini\config\mcp_config.json`

```json
{
  "mcpServers": {
    "rea": {
      "command": "npx",
      "args": ["-y", "rea-agents@latest", "mcp-server"],
      "env": {
        "REA_MCP_INPUT_SCHEMA_PROFILE": "compact"
      }
    }
  }
}
```

### 4.2 REA 워크플로 스킬(Skill) 설치
터미널에서 npx skills를 사용하여 에이전트 지침 스킬을 추가합니다:
```powershell
npx skills add morluto/rea --skill reverse-engineer-anything
```

---

## 5. 설치 상태 검증 (Health Check)

설치가 완료되면 REA의 진단 도구(`doctor`)를 통해 Antigravity와의 연결 상태를 점검합니다.

```powershell
npx -y rea-agents@latest doctor --client antigravity
```

- 모든 항목이 정상(Healthy)으로 확인되면 Antigravity IDE/앱을 재시작합니다.
- Antigravity 대화창 우측의 **Additional Options (...) > MCP Servers**에서 `rea`가 활성화되어 있는지 확인하실 수 있습니다.

---

## 6. 분석 엔진 요구사항 (선택 사항)

분석하려는 대상 애플리케이션의 종류에 따라 필요한 추가 도구가 다릅니다:

| 대상 (Target) | 필요 도구 | 비고 |
| :--- | :--- | :--- |
| **웹사이트 / JS / Electron 앱** | **추가 도구 불필요** | REA 자체 내장 정적 분석기로 즉시 분석 가능 |
| **.NET 어셈블리** | ilspycmd 등 | 디컴파일 도구 필요 시 연동 |
| **네이티브 바이너리 (EXE, DLL, ELF)** | **Ghidra**, **Hopper**, 또는 **IDA Pro** | Ghidra(무료 오픈소스) 또는 Hopper 설치 권장 |

---

## 7. Antigravity에서 REA 활용 예시

Antigravity에게 평소처럼 자연어로 리버스 엔지니어링 작업을 요청할 수 있습니다:

1. **JavaScript/Electron 앱 동작 분석**:
   ```text
   D:\Apps\TargetApp 폴더의 Electron 앱을 REA로 분석해서, 로그인 토큰 암호화 로직이 어떻게 구현되어 있는지 증거 코드와 함께 설명해줘.
   ```

2. **바이너리 기능 분석 및 재구현**:
   ```text
   이 실행 파일(sample.exe)의 패킷 인코딩 알고리즘을 분석하고, 동일하게 동작하는 파이썬 코드를 작성해줘.
   ```

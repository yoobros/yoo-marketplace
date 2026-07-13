# yoo-marketplace

개인용 Claude Code 플러그인 마켓플레이스입니다.

## 플러그인 목록

| 플러그인 | 설명 | 카테고리 |
|---------|------|---------|
| [marp-slides](./plugins) | Marp로 LaTeX/Mermaid/footnote가 포함된 슬라이드를 자연어로 생성·수정·빌드. 네이버 커스텀 테마 포함 | productivity |

## 설치 가이드

Claude Code 안에서는 `/plugin` 슬래시 커맨드로 인터랙티브하게 관리하고, 외부 셸에서는 `claude plugin ...` CLI를 사용합니다. 아래 각 단계에 두 가지 방법을 모두 적어두었습니다.

### 1. 마켓플레이스 등록

이 마켓플레이스를 Claude Code에 등록하면 포함된 모든 플러그인을 설치할 수 있습니다.

**Claude Code 안에서 (권장):**

```
/plugin marketplace add https://github.com/yoobros/yoo-marketplace
```

또는 인자 없이 `/plugin`만 실행하면 인터랙티브 UI가 뜨고, 거기서 `Add marketplace` 메뉴를 고를 수 있습니다.

**외부 셸에서 (CLI):**

```bash
claude plugin marketplace add https://github.com/yoobros/yoo-marketplace

# 로컬 경로에서 등록 (개발용)
claude plugin marketplace add /path/to/yoo-marketplace
```

등록 후 확인:

```
/plugin marketplace list        # Claude Code 안
claude plugin marketplace list  # 외부 셸
```

### 2. 플러그인 설치

마켓플레이스 등록이 완료되면, 개별 플러그인을 설치할 수 있습니다.

**Claude Code 안에서 (권장):**

```
/plugin install marp-slides@yoo-marketplace
```

**외부 셸에서 (CLI):**

```bash
# user scope (모든 프로젝트에서 사용)
claude plugin install marp-slides@yoo-marketplace

# project scope (현재 프로젝트에서만 사용)
claude plugin install marp-slides@yoo-marketplace --scope project
```

설치 후에는 Claude Code에서 `/reload-plugins`를 실행해 적용합니다.

### 3. 설치 확인

```
/plugin list        # Claude Code 안
claude plugin list  # 외부 셸
```

### 4. 플러그인 업데이트

마켓플레이스에 새 버전이 올라오면:

```
# Claude Code 안
/plugin marketplace update yoo-marketplace
/plugin update marp-slides

# 외부 셸
claude plugin marketplace update yoo-marketplace
claude plugin update marp-slides
```

### 5. 플러그인 제거

```
/plugin uninstall marp-slides        # Claude Code 안
claude plugin uninstall marp-slides  # 외부 셸
```

## Codex 등 다른 하네스에서 쓰기

스킬은 [agentskills.io](https://agentskills.io/specification) 스펙(`SKILL.md` + frontmatter)을
따르므로 Claude Code 전용이 아니다. Codex CLI · Copilot CLI · Gemini CLI 는 공통으로
`~/.agents/skills/` 를 스킬 디렉토리로 인식한다.

### 1. 스킬 연결 (symlink 권장 — 저장소 수정이 즉시 반영)

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/yoo-marketplace/plugins/skills/marp-slides ~/.agents/skills/marp-slides
```

### 2. 동작 확인

```bash
codex exec --skip-git-repo-check "너에게 로드된 skill 목록에 marp-slides 가 있는지 확인해줘"
```

세션 시작 시 frontmatter(name/description)가 스캔되고, 슬라이드 관련 요청이 오면
본문이 로드된다. 별도 활성화 명령은 없다. 안 잡히면 프롬프트에 "marp-slides skill 을
따라서" 를 명시하면 강제 로드된다.

### 3. Codex 사용 시 주의 (실측 기준, codex-cli 0.144)

- **`codex exec` 기본 샌드박스는 read-only** — 파일 생성이 조용히 차단된다.
  프로젝트 생성 작업은 `codex exec --sandbox workspace-write ...` 로 실행할 것.
- **비대화형인데 질문하고 종료할 수 있다** (청중/테마 확인 등). exec 모드에선
  프롬프트에 "질문하지 말고 스킬의 기본값으로 진행해" 를 붙이는 게 안전하다.
- 샌드박스에서 네트워크가 막히면 `npm install` 과 mermaid CDN 이 실패한다 —
  network access 를 허용하거나 스킬의 `references/mermaid-pdf.md` 로컬 vendoring 절차 사용.

검증된 시나리오: symlink 연결 → `codex exec --sandbox workspace-write` 로 새 덱
프로젝트 생성 → 템플릿 복사(레이아웃 유틸리티·`--html` preview·`htmlLabels:false`
포함) 정상 확인.

## 개발 가이드

### 로컬에서 플러그인 테스트

개발 중인 플러그인을 설치 없이 바로 테스트하려면 `--plugin-dir` 옵션을 사용합니다:

```bash
claude --plugin-dir ./plugins
```

### 플러그인 유효성 검사

```bash
# 개별 플러그인 검증
claude plugin validate ./plugins

# 마켓플레이스 전체 검증
claude plugin validate .
```

### 디렉토리 구조

```
yoo-marketplace/
├── .claude-plugin/
│   └── marketplace.json        # 마켓플레이스 정의
├── plugins/
│   ├── .claude-plugin/
│   │   └── plugin.json         # marp-slides 플러그인 메타데이터
│   └── skills/
│       └── marp-slides/
│           ├── SKILL.md        # 스킬 정의
│           ├── assets/         # 네이버 커스텀 테마 리소스
│           └── evals/
│               └── evals.json
└── README.md
```

### 새 플러그인 추가

1. `plugins/<plugin-name>/` 디렉토리 생성
2. `.claude-plugin/plugin.json` 작성
3. `skills/<skill-name>/SKILL.md` 작성
4. `.claude-plugin/marketplace.json`의 `plugins` 배열에 항목 추가
5. `claude plugin validate .`로 검증

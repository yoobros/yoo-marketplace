# 편집 가능한 LaTeX 수식

편집형 PPTX의 LaTeX는 PowerPoint 수식 편집기에서 수정할 수 있는 Office Math(OMML) 객체로
보존한다. 이 산출물 계약은 Codex와 Claude Code에 동일하며, 사용하는 생성 도구만 다르다.

## 허용 표현

- PowerPoint 슬라이드 XML의 `a14:m` 안에 `m:oMath` 또는 `m:oMathPara`가 들어 있는 네이티브
  Office Math(OMML) 객체
- 수식의 의미 구조(분수, 첨자, 근호, 합·적분, 행렬 등)를 보존한 객체
- 원본 LaTeX는 발표자 노트나 빌드 소스에도 남겨 재현 가능하게 한다.

SVG/PNG, 수식 스크린샷, 일반 텍스트, 유니코드 기호 조합은 편집 가능한 수식으로 인정하지
않는다. 보이지 않는 OMML과 그림을 겹쳐 놓는 방식도 실제 수식 편집성을 대신하지 못한다.

## 런타임별 생성

Codex의 artifact-tool과 Claude Code의 PptxGenJS 4.0.1에는 현재 문서화된 네이티브 수식 API가
없다. 따라서 두 런타임 모두 기본 네이티브 덱을 만든 뒤 다음 중 검증된 경로를 사용한다.

1. PowerPoint 자동화로 삽입한 Office Math 객체
2. Microsoft의 PresentationML 구조처럼 `mc:AlternateContent`의 `mc:Choice`에 `a14:m`과
   OMML을 넣는 검증된 OOXML 후처리
3. Microsoft 365가 지원하는 Presentation MathML을 Office Math로 가져온 뒤 저장하는 자동화

직접 XML 후처리를 구현할 때는 PowerPoint가 만든 수식 fixture를 기준으로 관계, namespace,
shape ID, fallback과 콘텐츠 타입을 보존하고 ZIP을 원자적으로 다시 작성한다. 단순 문자열
치환으로 슬라이드 XML에 `m:oMath` 태그만 추가하지 않는다.

## 검증 계약

Marp 원본에서 인라인·블록 LaTeX 수식을 세어 `N`으로 기록한 뒤 다음을 모두 수행한다.

```bash
python3 <스킬디렉토리>/scripts/inspect_editability.py dist/slides.pptx \
  --require-editable --require-equations N
```

1. 구조 검사에서 `equations >= N`이고 해당 슬라이드에 `m:oMath`가 존재한다.
2. Microsoft PowerPoint에서 각 수식을 더블클릭했을 때 **PowerPoint에서 수식 편집 모드**가
   열리고 분수·첨자·행렬 등 구조 단위를 수정할 수 있다.
3. 저장 후 다시 열어도 수식 객체와 레이아웃이 유지된다.
4. 모든 슬라이드를 다시 렌더해 잘림, 겹침, 기준선 불일치와 폰트 대체를 확인한다.

LibreOffice 렌더만으로 PowerPoint의 수식 편집성을 판정하지 않는다. PowerPoint 검증 환경이
없거나 변환이 실패하면 완전 편집형이라고 보고하지 않는다. 제한을 사용자에게 알리고 환경을
확보하거나, 사용자가 명시적으로 동의한 경우에만 해당 수식에 한해 비편집형 대체를 제공한다.
비편집형으로 자동 폴백하지 않는다.

참고: Microsoft의 PresentationML 수식 예시는 `a14:m` 안에 `m:oMathPara`/`m:oMath`를 두며,
Microsoft 365는 Presentation MathML을 Office Math로 가져올 수 있다.

- [Microsoft PresentationML Math 구조](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-odrawxml/38b13e1f-1102-4bb7-819a-dd5d9abdb176)
- [Microsoft 365 MathML 지원](https://learn.microsoft.com/en-us/office/math/mathml)

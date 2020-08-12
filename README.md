# GLOim Google Calendar 출근부 연동 프로그램

## #1.조교 목록 수정
1. `staffs.txt` 파일에서 `조교이름 직급:출근부 링크` 로 행을 추가합니다.
- ex) `전진호 조교:1ZQETW0R8bbfSdH-PELVUCl-4D5KUGQ6wpQkqwdUqcm8`

2. 직원명은 구글 캘린더에 기록되는 이름으로 작성되어야 합니다.

## #2 구글 캘린더 기록
1. `조교이름 직급 (본)` 또는 `조교이름 직급 (스)`로 작성합니다.
- ex) `전진호 조교 (본)`, `양서경 주임 (본)`

2. 휴게 시간은 `조교이름 직급 휴게`로 기록합니다.
- ex) `전진호 조교 휴게`

## #3 포인트 및 식대 수정
`sma_sheets.py`의 86~88번 째 줄을 수정합니다.

````python
    content = ['1,000', '', '', '본' if is_head else '',
               hour, hourly_wage, '식대' if is_lunch_included else '', '', '6,000' if is_lunch_included else '']
````
- `1,000` : 일괄 지급 포인트
- `6,000` : 일괄 지급 식대





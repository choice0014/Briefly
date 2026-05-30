@echo off
chcp 65001 > nul

echo ========================================
echo  GitHub 코드 업로드 자동화 스크립트
echo ========================================

if not exist .git (
    echo [1/5] Git 저장소 초기화 중...
    git init
    git remote add origin https://github.com/choice0014/Briefly.git
    git branch -M main
)

:: 현재 브랜치명 동적 감지
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
if "%BRANCH%"=="" set BRANCH=develop

echo 현재 작업 브랜치: %BRANCH%

echo [2/5] 원격 변경사항(%BRANCH%) 가져오는 중...
git pull --rebase origin %BRANCH%

echo [3/5] 변경된 파일 추가 중...
git add .

echo [4/5] 커밋 메시지 작성 중...
set /p msg="커밋 메시지를 입력하세요 (기본값: Update): "
if "%msg%"=="" set msg=Update

git commit -m "%msg%" || echo 커밋할 변경사항 없음

echo [5/5] GitHub로 업로드 중...
git push origin %BRANCH%

echo ========================================
echo  %BRANCH% 브랜치 업로드 완료
echo ========================================
pause